"""Catalogue access + the tools the DD agent can call.

All reads use a read-only SQLite connection, so the agent can never change the shop's data.
"""

import json
import sqlite3
from pathlib import Path

import re

from models import (
    Product,
    ProductFacts,
    ProductMatch,
    ProductNotFound,
    ProductSearchResults,
    AlternativeItem,
    Alternatives,
    SizeStock,
    SizeStockCheck,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_RESULTS = 12  # cards shown on the page for one search
LOW_STOCK = 3  # 1-3 units left counts as "low stock"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def load_inventory(conn: sqlite3.Connection) -> dict[str, list[SizeStock]]:
    stock: dict[str, list[SizeStock]] = {}
    for row in conn.execute("SELECT product_id, size, quantity FROM inventory"):
        stock.setdefault(row["product_id"], []).append(
            SizeStock(size=row["size"], quantity=row["quantity"])
        )
    for sizes in stock.values():
        sizes.sort(key=lambda s: SIZE_ORDER.index(s.size) if s.size in SIZE_ORDER else 99)
    return stock


def row_to_product(row: sqlite3.Row, inventory: list[SizeStock]) -> Product:
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        search_tags=json.loads(row["search_tags"]),
        image_file_path=row["image_file_path"],
        image_url=f"/media/{row['image_file_path']}",
        price=row["price"],
        inventory=inventory,
        total_stock=sum(s.quantity for s in inventory),
    )


def all_products() -> list[Product]:
    with get_db() as conn:
        stock = load_inventory(conn)
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    return [row_to_product(r, stock.get(r["product_id"], [])) for r in rows]


def products_by_ids(product_ids: list[str]) -> list[Product]:
    """Product cards in the given order; unknown ids are dropped."""
    by_id = {p.product_id: p for p in all_products()}
    seen: set[str] = set()
    cards = []
    for pid in product_ids:
        if pid in by_id and pid not in seen:
            seen.add(pid)
            cards.append(by_id[pid])
    return cards


# ---------- agent tools ----------


def _matches_type(product: Product, garment_type: str) -> bool:
    # garment_type values are inconsistent free text (e.g. "short-sleeve T-shirt" vs "t-shirt").
    want = garment_type.lower().replace("-", "").replace(" ", "").removesuffix("s")
    have = product.garment_type.lower().replace("-", "").replace(" ", "")
    aliases = {"tee": "tshirt", "hoodie": "hood", "1/4zip": "quarterzip", "fleece": "fleece"}
    want = aliases.get(want, want)
    # "short-sleeve crew-neck t-shirt" is a T-shirt, not a crewneck sweatshirt.
    # (Word match: "sweatshirt" also contains the letters "tshirt".)
    is_tee = bool(re.search(r"\bt[- ]?shirt", product.garment_type.lower()))
    if want == "tshirt":
        return is_tee
    if is_tee and "shirt" not in want:
        return False
    return want in have


def search_products(
    keywords: str = "",
    garment_type: str = "",
    color: str = "",
    size: str = "",
    max_price: float | None = None,
) -> ProductSearchResults:
    """Search the catalogue. All filters are optional and combined with AND.
    keywords match name, description, colours and tags (every word must appear).
    Returns the total match count and up to MAX_RESULTS matches, items with more stock first."""
    # Compare letters/digits only, so "1/4 zip" matches "Branford 1 4 Zip" and "T-shirt" matches "T shirt".
    words = re.findall(r"[a-z0-9]+", keywords.lower())
    size = normalize_size(size) if size.strip() else ""
    results = []
    for p in all_products():
        text = " ".join(
            re.findall(r"[a-z0-9]+", " ".join([p.name, p.garment_type, p.description, *p.colors, *p.search_tags]).lower())
        )
        if words and not all(w in text for w in words):
            continue
        if garment_type and not _matches_type(p, garment_type):
            continue
        if color and not any(color.lower() in c.lower() for c in p.colors):
            continue
        if max_price is not None and p.price > max_price:
            continue
        in_stock = [s.size for s in p.inventory if s.quantity > 0]
        if size and size not in in_stock:
            continue
        results.append(_to_match(p))
    results.sort(key=lambda m: -m.total_stock)
    filters = {"keywords": keywords, "garment_type": garment_type, "color": color, "size": size}
    if max_price is not None:
        filters["max_price"] = f"{max_price:g}"
    return ProductSearchResults(
        filters_used={k: v for k, v in filters.items() if v},
        total_matches=len(results),
        matches=results[:MAX_RESULTS],
    )


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def find_product(product_ref: str) -> Product | None:
    """Accept a product_id or a product name (case/punctuation-insensitive)."""
    ref = _slug(product_ref)
    products = all_products()
    for p in products:
        if p.product_id == product_ref.strip() or _slug(p.product_id) == ref or _slug(p.name) == ref:
            return p
    return None


def _to_match(p: Product) -> ProductMatch:
    return ProductMatch(
        product_id=p.product_id,
        name=p.name,
        garment_type=p.garment_type,
        colors=p.colors,
        price=p.price,
        sizes_in_stock=[s.size for s in p.inventory if s.quantity > 0],
        total_stock=p.total_stock,
    )


def suggest_similar(query: str, limit: int = 5) -> list[ProductMatch]:
    """Closest real products to a query that matched nothing exactly.
    Words found in most products (e.g. "yale") are ignored; a match on the garment type
    ("jacket", "hoodie") counts double, so suggestions are the same kind of item."""
    products = all_products()
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    texts = {
        p.product_id: set(re.findall(r"[a-z0-9]+", " ".join([p.name, *p.search_tags, *p.colors]).lower()))
        for p in products
    }
    types = {p.product_id: set(re.findall(r"[a-z0-9]+", p.garment_type.lower())) for p in products}
    common = {w for w in words if sum(w in t for t in texts.values()) > len(products) / 2}
    words -= common
    scored = []
    for p in products:
        score = sum(w in texts[p.product_id] for w in words) + 2 * sum(w in types[p.product_id] for w in words)
        if score:
            scored.append((score, p.total_stock, p))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [_to_match(p) for _, _, p in scored[:limit]]


def _not_found(product_ref: str) -> ProductNotFound:
    return ProductNotFound(
        query=product_ref,
        message="No product matches this exactly. Do not guess; offer the suggestions (if any) or ask the shopper.",
        suggestions=suggest_similar(product_ref),
    )


SIZE_ALIASES = {
    "XS": "XS", "XSMALL": "XS", "EXTRASMALL": "XS",
    "S": "S", "SM": "S", "SMALL": "S",
    "M": "M", "MD": "M", "MED": "M", "MEDIUM": "M",
    "L": "L", "LG": "L", "LARGE": "L",
    "XL": "XL", "XLARGE": "XL", "EXTRALARGE": "XL",
    "XXL": "XXL", "2XL": "XXL", "XXLARGE": "XXL", "2XLARGE": "XXL",
}


def normalize_size(size: str) -> str:
    key = re.sub(r"[^A-Z0-9]", "", size.upper())
    return SIZE_ALIASES.get(key, key)


def get_product_details(product_ref: str) -> ProductFacts | ProductNotFound:
    """Description, colours, price, total stock and stock per size for one product."""
    p = find_product(product_ref)
    if p is None:
        return _not_found(product_ref)
    return ProductFacts(
        product_id=p.product_id,
        name=p.name,
        garment_type=p.garment_type,
        description=p.description,
        colors=p.colors,
        price=p.price,
        stock_by_size={s.size: s.quantity for s in p.inventory},
        total_stock=p.total_stock,
        sizes_in_stock=[s.size for s in p.inventory if s.quantity > 0],
        sizes_sold_out=[s.size for s in p.inventory if s.quantity == 0],
    )


def _family(garment_type: str) -> str:
    t = garment_type.lower()
    if re.search(r"\bt[- ]?shirt", t) or "performance shirt" in t:
        return "tee"
    for key in ("hood", "quarter-zip", "jacket", "crewneck", "mockneck"):
        if key in t:
            return {"hood": "hoodie", "mockneck": "crewneck"}.get(key, key)
    return t


def find_alternatives(product_ref: str, size: str, limit: int = 6) -> Alternatives | ProductNotFound:
    """Similar items (same garment family) that are in stock in `size`, closest first:
    more shared colours, then nearer price, then more stock."""
    base = find_product(product_ref)
    if base is None:
        return _not_found(product_ref)
    wanted = normalize_size(size)
    base_colors = {c.lower() for c in base.colors}
    scored = []
    for p in all_products():
        if p.product_id == base.product_id or _family(p.garment_type) != _family(base.garment_type):
            continue
        qty = next((s.quantity for s in p.inventory if s.size == wanted), 0)
        if qty <= 0:
            continue
        shared = [c for c in p.colors if c.lower() in base_colors]
        scored.append((-len(shared), abs(p.price - base.price), -qty, p, qty, shared))
    scored.sort(key=lambda x: x[:3])
    return Alternatives(
        for_product=base.name,
        size=wanted,
        alternatives=[
            AlternativeItem(
                product_id=p.product_id,
                name=p.name,
                garment_type=p.garment_type,
                price=p.price,
                quantity_in_size=qty,
                shared_colors=shared,
            )
            for *_, p, qty, shared in scored[:limit]
        ],
    )


def check_size_stock(product_ref: str, size: str) -> SizeStockCheck | ProductNotFound:
    """Exact stock for one product in one size, read from the inventory table."""
    p = find_product(product_ref)
    if p is None:
        return _not_found(product_ref)
    wanted = normalize_size(size)
    row = next((s for s in p.inventory if s.size == wanted), None)
    quantity = row.quantity if row else 0
    if row is None:
        status = "size_not_offered"
    elif quantity == 0:
        status = "sold_out"
    elif quantity <= LOW_STOCK:
        status = "low_stock"
    else:
        status = "in_stock"
    return SizeStockCheck(
        product_id=p.product_id,
        name=p.name,
        size=wanted,
        quantity=quantity,
        status=status,
        price=p.price,
        other_sizes_in_stock=[s.size for s in p.inventory if s.quantity > 0 and s.size != wanted],
    )
