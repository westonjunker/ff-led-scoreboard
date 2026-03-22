"""BDF font loader with PIL conversion and in-memory caching."""

import os
from PIL import BdfFontFile, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")
_cache = {}


def _load_bdf(name):
    if name in _cache:
        return _cache[name]
    bdf_path = os.path.join(FONTS_DIR, f"{name}.bdf")
    pil_path = os.path.join(FONTS_DIR, f"{name}.pil")
    if not os.path.exists(pil_path):
        with open(bdf_path, "rb") as fp:
            bdf = BdfFontFile.BdfFontFile(fp)
            bdf.save(pil_path)
    font = ImageFont.load(pil_path)
    _cache[name] = font
    return font


def font_5x8():
    """5×8 — good for scores and labels in a 32px-wide quadrant."""
    try:
        return _load_bdf("5x8")
    except (FileNotFoundError, PermissionError, OSError):
        return ImageFont.load_default()


def font_4x6():
    """4×6 — compact, fits 4+ rows in a 32px-tall quadrant."""
    try:
        return _load_bdf("4x6")
    except (FileNotFoundError, PermissionError, OSError):
        return ImageFont.load_default()
