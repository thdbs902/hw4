"""Crop the real Yale college / school crests printed on CC's own product photos.

For each college or school, takes the product photo with the biggest crest, finds the most
saturated (colourful) cluster - the crest - and saves a square crop to data/brand/crests/.
Uses the cleaned photos in data/products_clean/. Output stays in data/ (git-ignored).

Run:  .venv/bin/python crop_crests.py
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SRC = DATA_DIR / "products_clean"
OUT = DATA_DIR / "brand" / "crests"

# crest id -> product photo with the clearest crest (largest print first)
SOURCES = {
    "benjamin-franklin": "benjamin-franklin-t-shirt.jpg",
    "berkeley": "berkeley-1-4-zip.jpg",
    "branford": "branford-1-4-zip.jpg",
    "davenport": "davenport-college-crewneck.jpg",
    "grace-hopper": "grace-hopper-logo-t-shirt.jpg",
    "jonathan-edwards": "jonathan-edwards-college-crewneck.jpg",
    "morse": "morse-logo-t-shirt.jpg",
    "pierson": "pierson-logo-t-shirt.jpg",
    "saybrook": "saybrook-logo-t-shirt.jpg",
    "timothy-dwight": "timothy-dwight-college-crewneck.jpg",
    "trumbull": "trumbull-1-4-zip.jpg",
    "law": "yale-law-school-1-4-zip.jpg",
    "management": "school-of-management-crest-t-shirt.jpg",
    "medicine": "school-of-medicine-1-4-zip.jpg",
    "nursing": "school-of-nursing-crest-t-shirt.jpg",
    "public-health": "school-of-public-health-1-4-zip.jpg",
    "divinity": "divinity-school-fleece-sweater.jpg",
    "art": "school-of-art-1-4-zip.jpg",
    "music": "school-of-music-fleece-sweater.jpg",
    "architecture": "school-of-architecture-crewneck.jpg",
    "engineering": "school-of-engineering-1-4-zip.jpg",
}

SATURATION_MIN = 70  # max-min channel spread that counts as "crest colour"
SIZE = 160


def crest_box(img: Image.Image, sat_min: int = SATURATION_MIN) -> tuple[int, int, int, int] | None:
    a = np.asarray(img).astype(int)
    sat = a.max(axis=2) - a.min(axis=2)
    navy_like = (a[:, :, 2] > a[:, :, 0]) & (a[:, :, 0] < 70)  # garment navy isn't crest
    mask = (sat >= sat_min) & ~navy_like
    mask[: int(img.height * 0.22)] = False  # skip the collar, where the blue brand tag sits
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
    arr = np.asarray(m) > 0
    if arr.sum() < 30:
        return None
    # largest cluster: keep pixels within the densest region via column/row projections
    ys, xs = np.where(arr)
    cy, cx = np.median(ys), np.median(xs)
    keep = (np.abs(ys - cy) < img.height * 0.2) & (np.abs(xs - cx) < img.width * 0.2)
    ys, xs = ys[keep], xs[keep]
    return xs.min(), ys.min(), xs.max(), ys.max()


def dark_crest_box(img: Image.Image) -> tuple[int, int, int, int] | None:
    """Black/charcoal crest on a light (heather gray) garment, e.g. Davenport, Trumbull."""
    a = np.asarray(img).astype(int)
    dark = a.max(axis=2) < 70
    h, w = dark.shape
    dark[: int(h * 0.22)] = False  # collar / tag
    dark[:, : int(w * 0.25)] = False  # sleeves and seams on the sides
    dark[:, int(w * 0.85) :] = False
    dark[int(h * 0.75) :] = False
    ys, xs = np.where(dark)
    if ys.size < 30:
        return None
    # Densest spot: the crest is a solid dark block, the name text below it is thin.
    grid = np.zeros((h // 8 + 1, w // 8 + 1))
    np.add.at(grid, (ys // 8, xs // 8), 1)
    gy, gx = np.unravel_index(grid.argmax(), grid.shape)
    cy, cx = gy * 8 + 4, gx * 8 + 4
    keep = (np.abs(ys - cy) < h * 0.06) & (np.abs(xs - cx) < w * 0.06)
    ys, xs = ys[keep], xs[keep]
    return xs.min(), ys.min(), xs.max(), ys.max()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for crest_id, photo in SOURCES.items():
        img = Image.open(SRC / photo).convert("RGB")
        box = crest_box(img) or crest_box(img, sat_min=35) or dark_crest_box(img)
        if box is None:
            print("no crest found:", crest_id)
            continue
        x0, y0, x1, y1 = box
        side = int(max(x1 - x0, y1 - y0) * 1.25) + 4
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        crop = img.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
        crop.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{crest_id}.png")
        print(f"{crest_id}: {photo} box={box}")


if __name__ == "__main__":
    main()
