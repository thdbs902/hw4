"""Append-only audit trail of DD's agent loop: output/audit_trail.json (Problem 12).

The file is one JSON array. New entries are appended in place (seek to the closing "]",
write ", {...}\n]"), so earlier entries are never rewritten or wiped between runs or restarts.
No passwords, password hashes, session cookies or API keys are ever written here.
"""

import json
import os
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
PREVIEW_CHARS = 200  # args / result previews are cut to this length
_lock = threading.Lock()


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def new_run_id() -> str:
    return uuid.uuid4().hex[:8]


def preview(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= PREVIEW_CHARS else text[: PREVIEW_CHARS - 1] + "…"


def append(entries: list[dict[str, Any]]) -> None:
    """Append entries to the JSON array without touching earlier ones."""
    if not entries:
        return
    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        body = ",\n".join(json.dumps(e, ensure_ascii=False) for e in entries)
        if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
            AUDIT_PATH.write_text("[\n" + body + "\n]\n", encoding="utf-8")
            return
        with open(AUDIT_PATH, "rb+") as f:
            # Find the final "]" and write the new entries just before it.
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            while pos > 0:
                pos -= 1
                f.seek(pos)
                ch = f.read(1)
                if ch == b"]":
                    break
            f.seek(pos)
            prev = pos - 1
            while prev > 0:
                f.seek(prev)
                c = f.read(1)
                if not c.isspace():
                    break
                prev -= 1
            sep = "\n" if c == b"[" else ",\n"  # empty array vs existing entries
            f.seek(pos)
            f.write((sep + body + "\n]\n").encode("utf-8"))
            f.truncate()
