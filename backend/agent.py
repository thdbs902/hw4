"""DD — the Campus Customs shop agent (PydanticAI), wired for FastAPI.

- Model: gpt-5.6-luna (OpenAI) through Portkey, using PORTKEY_API_KEY.
- System prompt: prompts/prompt.md
- Tools: tools.py   - Types: models.py
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext  # noqa: E402
from pydantic_ai.exceptions import ModelHTTPError, UsageLimitExceeded
from pydantic_ai.usage import UsageLimits
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

import audit
import preferences
import tools
from models import (
    ChatReply,
    ChatTurn,
    CustomerInfo,
    PageContext,
    Alternatives,
    ShopperPreferences,
    ProductFacts,
    ProductNotFound,
    ProductSearchResults,
    ShopReply,
    SizeStockCheck,
)

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"
MODEL_NAME = os.getenv("CC_MODEL", "gpt-5.6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")

# Loop limits for one chat turn (Problem 12). A normal turn uses 2-4 model requests.
LIMITS = UsageLimits(request_limit=8, tool_calls_limit=12, total_tokens_limit=60_000)
LIMIT_REPLY = "Sorry, that one took me too many steps. Could you ask about one item or one type at a time?"

log = logging.getLogger("uvicorn.error")


def build_model() -> OpenAIResponsesModel:
    """gpt-5.6-luna through Portkey's OpenAI-compatible gateway (Responses API, supports tools)."""
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is not set (checked HW4/.env and YALE/.env)")
    client = AsyncOpenAI(
        api_key=key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))


@dataclass
class ShopDeps:
    """Per-request context for DD (PydanticAI deps). No passwords or hashes, ever."""

    customer: CustomerInfo | None  # None = guest
    page: PageContext | None
    preferences: ShopperPreferences | None = None  # logged-in shoppers only
    db_path: str = ""


def build_agent() -> Agent[ShopDeps, ShopReply]:
    dd = Agent(
        build_model(),
        deps_type=ShopDeps,
        output_type=ShopReply,
        system_prompt=PROMPT_PATH.read_text(encoding="utf-8"),
        name="DD",
    )

    @dd.instructions
    def who_and_where(ctx: RunContext[ShopDeps]) -> str:
        """Added to the prompt on every run: who is chatting and what page they're on."""
        c, page = ctx.deps.customer, ctx.deps.page
        lines = ["# This conversation"]
        if c:
            lines.append(f"- Shopper: logged in as {c.first_name} {c.last_name} ({c.email}).")
        else:
            lines.append("- Shopper: a guest (not logged in). You don't know their name or email.")
        prefs = ctx.deps.preferences
        if c and prefs and (prefs.size or prefs.colors):
            lines.append(
                f"- Remembered preferences: usual size {prefs.size or 'unknown'}; "
                f"favourite colours {', '.join(prefs.colors) or 'unknown'}. Use the size when they don't name one."
            )
        elif c:
            lines.append("- No remembered size yet. If they mention their size, save it with `remember_preferences`.")
        if page and page.product_id and page.product_name:
            lines.append(
                f'- They are viewing the product page for "{page.product_name}" '
                f"(product_id: {page.product_id}). \"this\", \"it\" or \"this one\" means this product "
                "unless they clearly mean something else."
            )
        elif page:
            lines.append(f"- They are on the page {page.path}.")
        return "\n".join(lines)

    @dd.tool_plain
    def search_products(
        keywords: str = "",
        garment_type: str = "",
        color: str = "",
        size: str = "",
        max_price: float | None = None,
    ) -> ProductSearchResults:
        """Search the CC catalogue. All filters optional. Returns total_matches and up to 12
        structured matches; the ones you put in product_ids are shown as cards on the page.

        Args:
            keywords: words that must all appear in name/description/tags, e.g. "baseball", "Branford", "dad".
            garment_type: e.g. "hoodie", "crewneck", "t-shirt", "quarter-zip", "fleece jacket".
            color: e.g. "navy", "gray", "white".
            size: only items in stock in this size (XS, S, M, L, XL, XXL).
            max_price: highest price in USD.
        """
        return tools.search_products(keywords, garment_type, color, size, max_price)

    @dd.tool_plain
    def get_product_details(product: str) -> ProductFacts | ProductNotFound:
        """Description, colours, price, total stock and stock for every size of ONE product.
        Use for "tell me about…", "how much is…", "how many do you have…".

        Args:
            product: the product_id from search results (preferred) or the exact product name.
        """
        return tools.get_product_details(product)

    @dd.tool_plain
    def check_size_stock(product: str, size: str) -> SizeStockCheck | ProductNotFound:
        """Exact stock of ONE product in ONE size. Call this whenever the shopper names a size,
        before saying the item is available in it.

        Args:
            product: the product_id from search results (preferred) or the exact product name.
            size: XS, S, M, L, XL or XXL (words like "medium" or "2XL" are accepted).
        """
        return tools.check_size_stock(product, size)

    @dd.tool_plain
    def find_alternatives(product: str, size: str) -> Alternatives | ProductNotFound:
        """Similar items of the same type that ARE in stock in this size. Call it whenever a
        product is sold out (or not offered) in the size the shopper wants.

        Args:
            product: the sold-out product's product_id (preferred) or exact name.
            size: the size the shopper needs.
        """
        return tools.find_alternatives(product, size)

    @dd.tool
    def remember_preferences(
        ctx: RunContext[ShopDeps], size: str | None = None, colors: list[str] | None = None
    ) -> str:
        """Save a logged-in shopper's usual size and/or favourite colours for next time.
        Call it when they tell you their size ("I'm a medium") or a colour they love.

        Args:
            size: their usual size (XS, S, M, L, XL, XXL), if mentioned.
            colors: favourite colours, if mentioned.
        """
        if ctx.deps.customer is None:
            return "Guest shopper: preferences can't be saved. Suggest logging in to remember their size."
        current = ctx.deps.preferences or ShopperPreferences()
        updated = ShopperPreferences(
            size=tools.normalize_size(size) if size else current.size,
            colors=colors if colors else current.colors,
        )
        preferences.save(ctx.deps.db_path, ctx.deps.customer.user_id, updated)
        ctx.deps.preferences = updated
        return f"Saved: size {updated.size or '-'}, colours {', '.join(updated.colors) or '-'}."

    return dd


_agent: Agent[ShopDeps, ShopReply] | None = None


def get_agent() -> Agent[ShopDeps, ShopReply]:
    """Built once on first use (after .env is loaded) and reused for every request."""
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def _to_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    history: list[ModelMessage] = []
    for t in turns:
        if t.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=t.content)]))
        else:
            history.append(ModelResponse(parts=[TextPart(content=t.content)]))
    return history


BLOCKED_REPLY = (
    "I can't help with that one, but I'd love to help you find some Yale merch. "
    "Ask me about a hoodie, a size, or a price!"
)


def _is_content_filter(err: ModelHTTPError) -> bool:
    body = err.body if isinstance(err.body, dict) else {}
    return err.status_code == 400 and (
        body.get("code") == "content_filter" or "content management policy" in str(body)
    )


def _usage(obj):
    """RunUsage, whether this PydanticAI version exposes `usage` as a method or a property."""
    u = getattr(obj, "usage", None)
    return u() if callable(u) else u


def _redact(text: str) -> str:
    """Audit previews must not store card numbers or emails a shopper typed."""
    import re

    text = re.sub(r"\b(?:\d[ -]?){12,19}\b", "[number removed]", text)
    return re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email removed]", text)


def _audit_run(run_id: str, message: str, deps: ShopDeps, messages: list, stop_reason: str, usage=None) -> None:
    """Write one entry per tool call plus one run_end entry to output/audit_trail.json."""
    returns = {
        part.tool_call_id: part
        for msg in messages
        for part in getattr(msg, "parts", [])
        if part.part_kind == "tool-return"
    }
    who = f"user:{deps.customer.user_id}" if deps.customer else "guest"
    entries, iteration = [], 0
    for msg in messages:
        if not isinstance(msg, ModelResponse):
            continue
        iteration += 1
        for part in msg.parts:
            if part.part_kind != "tool-call":
                continue
            ret = returns.get(part.tool_call_id)
            entries.append(
                {
                    "time": (ret.timestamp if ret else msg.timestamp).isoformat(timespec="seconds"),
                    "run_id": run_id,
                    "event": "tool_call",
                    "iteration": iteration,
                    "tool_name": part.tool_name,
                    "args": audit.preview(part.args_as_dict()),
                    "result": audit.preview(ret.content if ret else "(no result)"),
                }
            )
    last = next((m for m in reversed(messages) if isinstance(m, ModelResponse)), None)
    entries.append(
        {
            "time": audit.now(),
            "run_id": run_id,
            "event": "run_end",
            "model": MODEL_NAME,
            "who": who,
            "page": (deps.page.product_id or deps.page.path) if deps.page else None,
            "message": audit.preview(_redact(message)),
            "iterations": iteration,
            "stop_reason": stop_reason,
            "model_finish_reason": getattr(last, "finish_reason", None),
            "requests": getattr(usage, "requests", None),
            "tool_calls": getattr(usage, "tool_calls", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    )
    audit.append(entries)


async def chat(message: str, history: list[ChatTurn], deps: ShopDeps) -> ChatReply:
    """One chat turn: run DD (within LIMITS), audit it, then attach product cards from the DB."""
    run_id = audit.new_run_id()
    dd = get_agent()
    try:
        async with dd.iter(message, message_history=_to_history(history), deps=deps, usage_limits=LIMITS) as run:
            try:
                async for _ in run:
                    pass
            except UsageLimitExceeded as err:
                _audit_run(run_id, message, deps, run.new_messages(), f"usage_limit: {err}", _usage(run))
                return ChatReply(reply=LIMIT_REPLY)
            result = run.result
    except ModelHTTPError as err:
        # gpt-5.6-luna is served via Azure OpenAI behind Portkey; its filter rejects some
        # jailbreak-style messages before the model sees them. Answer in DD's voice instead of failing.
        if _is_content_filter(err):
            _audit_run(run_id, message, deps, [], "content_filter")
            return ChatReply(reply=BLOCKED_REPLY, blocked=True)
        _audit_run(run_id, message, deps, [], f"error: HTTP {err.status_code}")
        raise
    out = result.output
    new_messages = result.new_messages()
    _audit_run(run_id, message, deps, new_messages, "final_result", _usage(result))
    calls = [
        f"{part.tool_name}({part.args_as_json_str()})"
        for msg in new_messages
        for part in getattr(msg, "parts", [])
        if part.part_kind == "tool-call" and part.tool_name != "final_result"
    ]
    log.info(
        "DD agent [%s] run=%s user=%s page=%s tools=%s products=%s",
        MODEL_NAME,
        run_id,
        "user:%s" % deps.customer.user_id if deps.customer else "guest",
        deps.page.product_id or deps.page.path if deps.page else "-",
        calls or "none",
        out.product_ids,
    )

    # Catalogue-wide count from the last search, so the page can say "12 of 26".
    searches = [
        part.content
        for msg in new_messages
        for part in getattr(msg, "parts", [])
        if part.part_kind == "tool-return" and isinstance(part.content, ProductSearchResults)
    ]
    products = tools.products_by_ids(out.product_ids[: tools.MAX_RESULTS])
    return ChatReply(
        reply=out.reply,
        products=products,
        results_title=out.results_title if products else "",
        total_matches=searches[-1].total_matches if products and searches else None,
    )
