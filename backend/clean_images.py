"""Make neat display copies of product images: black backgrounds -> white, garment cropped
and centred.

Many catalogue photos have a black background (with a light halo around the garment), black
side bars, or black gaps between the arms and the body, and garments fill their frames by
different amounts. For every product this script:
  1. paints white the near-black, colourless pixels connected to the image border (the
     background) and enclosed near-black gaps (e.g. under the arms). Products that list black
     or charcoal as a colour keep their enclosed dark areas, which may be part of the garment;
  2. smooths and feathers that mask so the garment outline is clean, not jagged;
  3. crops to the garment with even padding and centres it on a white square.

Originals in data/products/ are never modified. Cleaned copies go to data/products_clean/
(git-ignored with the rest of data/). The backend serves a cleaned copy when one exists.

Run:  .venv/bin/python clean_images.py
"""

import json
import sqlite3
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SRC_DIR = DATA_DIR / "products"
OUT_DIR = DATA_DIR / "products_clean"
DB_PATH = DATA_DIR / "campus_customs.db"

BLACK_MAX = 12  # background-black: every channel <= this...
NEUTRAL_MAX = 6  # ...and nearly grey (max - min channel), so dark navy shadows are kept
DARKISH_MAX = 60  # 1px fringe next to the background is also cleaned if this dark
MIN_GAP_AREA = 0.0015  # enclosed black gaps smaller than this share of the image are kept
PADDING = 0.06  # white margin around the cropped garment
# Photos whose shadow folds are pure black (looked like gaps): keep enclosed dark areas.
KEEP_DARK_FOLDS = {"basic-hoodie-big-yale.jpg"}
WHITE = (255, 255, 255)


def dark_colour_products() -> set[str]:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rows = conn.execute("SELECT image_file_path, colors FROM catalogue").fetchall()
    return {
        Path(path).name
        for path, colors in rows
        if any(w in c.lower() for c in json.loads(colors) for w in ("black", "charcoal"))
    }


RIM_LIGHT = 110  # mean brightness of the ring around a gap that marks a cut-out edge


def _has_light_rim(pixels: np.ndarray, region: np.ndarray) -> bool:
    """A real cut-out gap (e.g. under an arm) is outlined by the light halo left from the photo's
    cut-out; a dark shadow fold inside the garment is surrounded by dark fabric."""
    grown = np.asarray(Image.fromarray(region.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
    rim = grown & ~region
    return bool(rim.any()) and pixels[rim].max(axis=1).mean() >= RIM_LIGHT


def _is_sliver(region: np.ndarray) -> bool:
    """Gaps between an arm and the body are tall, thin slivers; a hood's dark inside is a blob."""
    ys, xs = np.where(region)
    height, width = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    fill_ratio = region.sum() / (height * width)
    return height >= 2.5 * width or fill_ratio < 0.35


def background_mask(img: Image.Image, remove_gaps: bool) -> Image.Image:
    w, h = img.size
    pixels = np.asarray(img)
    spread = pixels.max(axis=2).astype(int) - pixels.min(axis=2)
    is_black = (pixels <= BLACK_MAX).all(axis=2) & (spread <= NEUTRAL_MAX)
    mask = Image.fromarray(np.where(is_black, 255, 0).astype(np.uint8)).copy()

    # Background = near-black connected to the border (marked 128).
    border = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    border += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    for xy in border:
        if mask.getpixel(xy) == 255:
            ImageDraw.floodfill(mask, xy, 128)

    # Enclosed near-black regions big enough to be gaps (under arms, between sleeves) -> 128.
    if remove_gaps:
        min_area = MIN_GAP_AREA * w * h
        arr = np.asarray(mask)
        while (left := np.argwhere(arr == 255)).size:
            y, x = left[0]
            ImageDraw.floodfill(mask, (int(x), int(y)), 64)
            arr = np.asarray(mask)
            region = arr == 64
            is_gap = _has_light_rim(pixels, region) or _is_sliver(region)
            fill = 128 if region.sum() >= min_area and is_gap else 1
            arr = np.where(region, fill, arr).astype(np.uint8)
            mask = Image.fromarray(arr).copy()
    background = mask.point(lambda v: 255 if v == 128 else 0)

    # Grow by 1px to catch the dark JPEG fringe, but only over dark-ish pixels.
    darkish = Image.fromarray(np.where(pixels.max(axis=2) <= DARKISH_MAX, 255, 0).astype(np.uint8)).copy()
    background = Image.composite(background.filter(ImageFilter.MaxFilter(3)), background, darkish)

    # Smooth the outline (open/close + blur/threshold), keeping the hard mask for thin strips.
    smooth = background.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    smooth = smooth.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    smooth = smooth.filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v >= 110 else 0)
    return Image.fromarray(np.maximum(np.asarray(smooth), np.asarray(background)))


def crop_and_centre(img: Image.Image) -> Image.Image:
    """Crop to the non-white garment area, add even padding, centre on a white square."""
    arr = np.asarray(img)
    ys, xs = np.where(arr.min(axis=2) < 238)
    if ys.size == 0:
        return img
    box = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    side = int(max(box.size) * (1 + 2 * PADDING))
    canvas = Image.new("RGB", (side, side), WHITE)
    canvas.paste(box, ((side - box.width) // 2, (side - box.height) // 2))
    return canvas


def clean(path: Path, remove_gaps: bool) -> Image.Image:
    img = Image.open(path).convert("RGB")
    background = background_mask(img, remove_gaps)
    # Feather the edge so the outline blends into white instead of looking jagged.
    soft = background.filter(ImageFilter.GaussianBlur(1.2))
    soft = Image.fromarray(np.maximum(np.asarray(soft), np.asarray(background)))
    img.paste(WHITE, mask=soft)
    return crop_and_centre(img)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    keep_dark = dark_colour_products() | KEEP_DARK_FOLDS
    count = 0
    for path in sorted(SRC_DIR.glob("*.jpg")):
        clean(path, remove_gaps=path.name not in keep_dark).save(OUT_DIR / path.name, quality=92)
        count += 1
    print(f"{count} images cleaned and centred → {OUT_DIR} ({len(keep_dark)} kept enclosed dark areas)")


if __name__ == "__main__":
    main()
