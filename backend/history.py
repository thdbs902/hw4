"""Chat memory for logged-in shoppers, stored in the existing chat_messages table.

chat_messages(id, user_id → users.id, role 'user'|'assistant', content, products_json, created_at)
products_json holds the product cards shown with an assistant reply ('[]' when none), the same
shape as models.Product, so reloaded history can show its cards again.
"""

import json
import sqlite3

from models import ChatTurn, HistoryMessage, Product

HISTORY_FOR_AGENT = 12  # most recent turns given to the agent as context
HISTORY_FOR_PAGE = 50  # most recent turns shown in the chat widget


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load(db_path: str, user_id: int, limit: int = HISTORY_FOR_PAGE) -> list[HistoryMessage]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    messages = []
    for r in reversed(rows):
        try:
            products = [Product.model_validate(p) for p in json.loads(r["products_json"] or "[]")]
        except (ValueError, TypeError):
            products = []
        messages.append(
            HistoryMessage(role=r["role"], content=r["content"], products=products, created_at=r["created_at"])
        )
    return messages


def turns_for_agent(db_path: str, user_id: int) -> list[ChatTurn]:
    return [ChatTurn(role=m.role, content=m.content) for m in load(db_path, user_id, HISTORY_FOR_AGENT)]


def save_turn(db_path: str, user_id: int, message: str, reply: str, products: list[Product]) -> None:
    """Save the shopper's message and DD's reply together (one transaction)."""
    cards = json.dumps([p.model_dump() for p in products], ensure_ascii=False)
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
            (user_id, message),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply, cards),
        )
