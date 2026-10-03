"""Pydantic / PydanticAI structured types for the Campus Customs backend."""

from typing import Literal

from pydantic import BaseModel, Field

# ---------- products (Problem 3) ----------


class SizeStock(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    """Product card. Same shape as the cards already saved in chat_messages.products_json."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    image_file_path: str
    image_url: str
    price: float
    inventory: list[SizeStock]
    total_stock: int


# ---------- agent tool results (compact, to keep model tokens/cost low) ----------


class ProductMatch(BaseModel):
    """One search hit as the agent sees it (no long description)."""

    product_id: str
    name: str
    garment_type: str
    colors: list[str]
    price: float
    sizes_in_stock: list[str]
    total_stock: int


class ProductSearchResults(BaseModel):
    """Structured product matches for a catalogue search (search_products)."""

    filters_used: dict[str, str] = Field(description="The non-empty filters this search used.")
    total_matches: int = Field(description="How many catalogue items match in total.")
    matches: list[ProductMatch] = Field(description="Up to 12 matches, most in stock first.")


class ProductFacts(BaseModel):
    """Full facts for one product, including stock per size (get_product_details)."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    stock_by_size: dict[str, int]
    total_stock: int
    # Problem 6: pre-computed so the model doesn't have to read zeros out of stock_by_size.
    sizes_in_stock: list[str] = Field(default_factory=list)
    sizes_sold_out: list[str] = Field(default_factory=list)


StockStatus = Literal["in_stock", "low_stock", "sold_out", "size_not_offered"]


class SizeStockCheck(BaseModel):
    """Stock for one product in one size (check_size_stock)."""

    product_id: str
    name: str
    size: str = Field(description="Normalised size: XS, S, M, L, XL or XXL.")
    quantity: int = Field(description="Units in stock in this size; 0 = sold out.")
    status: StockStatus
    price: float
    other_sizes_in_stock: list[str] = Field(
        description="Sizes of the same product that are in stock, for suggesting alternatives."
    )


class ProductNotFound(BaseModel):
    """Returned instead of guessing when a lookup doesn't match a product."""

    query: str
    message: str
    suggestions: list[ProductMatch] = Field(default_factory=list)


# ---------- agent output ----------


class ShopReply(BaseModel):
    """What the DD agent returns. Product cards are built from the database
    using product_ids, so prices/stock shown on the page always come from SQLite."""

    reply: str = Field(description="Your answer to the shopper, in plain text (no Markdown).")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id values (from tool results) to show as product cards on the page, "
        "best first, max 12.",
    )
    results_title: str = Field(
        default="",
        description='Short heading for those cards, e.g. "Hoodies" or "Navy crewnecks under $60". '
        "Empty if product_ids is empty.",
    )


# ---------- chat API ----------


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class PageInfo(BaseModel):
    """What the shopper is looking at, sent by the front end with each message."""

    path: str = Field(default="/", max_length=200)
    product_id: str | None = Field(default=None, max_length=120)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    # Used for guests only; logged-in shoppers' history is loaded from chat_messages.
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)
    page: PageInfo | None = None


class HistoryMessage(BaseModel):
    """One saved chat_messages row, as returned to the chat widget."""

    role: Literal["user", "assistant"]
    content: str
    products: list[Product] = Field(default_factory=list)
    created_at: str


# ---------- agent deps (Problem 8) ----------


class CustomerInfo(BaseModel):
    """Who is chatting. Deliberately has NO password or password_hash field."""

    user_id: int
    first_name: str
    last_name: str
    email: str


class ShopperPreferences(BaseModel):
    """Remembered per logged-in shopper (Problem 9: remember shopper's size)."""

    size: str | None = Field(default=None, description="Usual size: XS, S, M, L, XL or XXL.")
    colors: list[str] = Field(default_factory=list, description="Favourite colours, e.g. ['navy'].")


class AlternativeItem(BaseModel):
    """A similar item that IS in stock in the requested size (Problem 9: find alternatives)."""

    product_id: str
    name: str
    garment_type: str
    price: float
    quantity_in_size: int
    shared_colors: list[str]


class Alternatives(BaseModel):
    for_product: str
    size: str
    alternatives: list[AlternativeItem]


class PageContext(BaseModel):
    """Current page, with the product name looked up from the DB (not trusted from the browser)."""

    path: str
    product_id: str | None = None
    product_name: str | None = None


class ChatReply(BaseModel):
    reply: str
    products: list[Product] = Field(default_factory=list)
    results_title: str = ""
    total_matches: int | None = Field(
        default=None, description="Catalogue-wide match count from the last search, if any."
    )
    blocked: bool = Field(
        default=False,
        description="True when the provider's safety filter blocked the message; "
        "the front end leaves blocked turns out of later history.",
    )
