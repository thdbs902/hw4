"""Campus Customs backend.

Problem 3: read-only product API + product images.
Problem 4: accounts (auth.py) - register/login write to the existing users table.
Problem 5: DD chat agent - POST /api/chat runs the PydanticAI agent (agent.py).

Run from backend/:  uvicorn main:app --reload --port 8000
"""

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

HW4_DIR = Path(__file__).resolve().parent.parent
load_dotenv(HW4_DIR / ".env")
load_dotenv(HW4_DIR.parent / ".env")  # root .env (PORTKEY_API_KEY)

# These modules read env vars (SESSION_SECRET, PORTKEY_API_KEY), so import after load_dotenv.
import agent  # noqa: E402
import auth  # noqa: E402
import history  # noqa: E402
import preferences  # noqa: E402
import tools  # noqa: E402
from models import (  # noqa: E402
    ChatReply,
    ChatRequest,
    CustomerInfo,
    HistoryMessage,
    PageContext,
    PageInfo,
    Product,
)

DATA_DIR = HW4_DIR / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"
CLEAN_DIR = DATA_DIR / "products_clean"  # black backgrounds turned white (clean_images.py)

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.build_router(str(DB_PATH)))


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Friendly messages only. FastAPI's default echoes the submitted input back,
    which would include passwords."""
    messages = []
    for err in exc.errors():
        field = str(err["loc"][-1]).replace("_", " ").capitalize()
        if err["type"] == "string_too_short":
            messages.append(f"{field} must be at least {err['ctx']['min_length']} characters.")
        elif err["type"] == "string_too_long":
            messages.append(f"{field} must be at most {err['ctx']['max_length']} characters.")
        elif err["type"] == "missing":
            messages.append(f"{field} is required.")
        else:
            messages.append(f"{field} is invalid.")
    return JSONResponse(status_code=422, content={"detail": " ".join(messages)})


BRAND_DIR = DATA_DIR / "brand"  # Yale shield (Wikimedia) + crests cropped by crop_crests.py


@app.get("/media/brand/{path:path}")
def brand_file(path: str) -> FileResponse:
    """Yale shield and college/school crests. Only files inside data/brand/ are served."""
    file = (BRAND_DIR / path).resolve()
    if BRAND_DIR.resolve() in file.parents and file.is_file() and file.suffix in {".svg", ".png"}:
        return FileResponse(file, headers={"Cache-Control": "public, max-age=3600"})
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/media/products/{filename}")
def product_image(filename: str) -> FileResponse:
    """image_file_path is relative to data/, e.g. products/x.jpg -> /media/products/x.jpg
    (matches image_url in saved chat history). Serves the cleaned copy when one exists.
    Only files directly inside the product folders are served, never the .db file."""
    for folder in (CLEAN_DIR, PRODUCTS_DIR):
        path = (folder / filename).resolve()
        if path.parent == folder.resolve() and path.is_file():
            return FileResponse(path, headers={"Cache-Control": "public, max-age=3600"})
    raise HTTPException(status_code=404, detail="Image not found")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products", response_model=list[Product])
def list_products() -> list[Product]:
    return tools.all_products()


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    cards = tools.products_by_ids([product_id])
    if not cards:
        raise HTTPException(status_code=404, detail="Product not found")
    return cards[0]


# ---------- chat (Problem 5) ----------


def _customer(cc_session: str | None) -> CustomerInfo | None:
    user = auth.get_current_user(str(DB_PATH), cc_session)
    if user is None:
        return None
    # Only these four fields reach the agent - never the password hash.
    return CustomerInfo(user_id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email)


def _page_context(page: PageInfo | None) -> PageContext | None:
    if page is None:
        return None
    product = tools.products_by_ids([page.product_id]) if page.product_id else []
    return PageContext(
        path=page.path,
        product_id=product[0].product_id if product else None,
        product_name=product[0].name if product else None,
    )


@app.get("/api/chat/history", response_model=list[HistoryMessage])
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[HistoryMessage]:
    """The logged-in shopper's saved chat (oldest first). Guests get []."""
    customer = _customer(cc_session)
    return history.load(str(DB_PATH), customer.user_id) if customer else []


@app.post("/api/chat", response_model=ChatReply)
async def chat(body: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatReply:
    """Website chat widget -> DD agent -> reply text + product cards from the DB.
    Logged in: history comes from chat_messages and the new turn is saved there.
    Guest: history comes from the browser and nothing is stored."""
    customer = _customer(cc_session)
    deps = agent.ShopDeps(
        customer=customer,
        page=_page_context(body.page),
        preferences=preferences.load(str(DB_PATH), customer.user_id) if customer else None,
        db_path=str(DB_PATH),
    )
    turns = history.turns_for_agent(str(DB_PATH), customer.user_id) if customer else body.history
    try:
        reply = await agent.chat(body.message, turns, deps)
    except Exception:
        log.exception("DD agent failed")
        raise HTTPException(
            status_code=502,
            detail="DD is having trouble answering right now. Please try again in a moment.",
        )
    # Blocked (content-filtered) turns are not saved, so they can't poison future history.
    if customer and not reply.blocked:
        history.save_turn(str(DB_PATH), customer.user_id, body.message, reply.reply, reply.products)
    return reply
