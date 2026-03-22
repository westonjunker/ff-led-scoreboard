"""Offseason display: scrolling league name, final finish position, countdown to kickoff."""

import datetime
from PIL import Image, ImageDraw
import fonts

SEASON_START = datetime.date(2026, 9, 4)
SCROLL_SPEED = 1          # px per tick
SCROLL_PAUSE_FRAMES = 60  # blank frames between scroll cycles (~3s at 20fps)

# ── Layout (32px tall) ────────────────────────────────────────────────────────
# y  0-9   (10px) : scrolling league name strip  — 5x8 font, 1px top pad
# y  10    ( 1px) : divider
# y  11-20 (10px) : rank ordinal centered        — 5x8 font, 1px top pad
# y  21    ( 1px) : divider
# y  22-31 (10px) : countdown centered           — 5x8 font, 1px top pad
# ─────────────────────────────────────────────────────────────────────────────

NAME_STRIP_H  = 10
RANK_Y        = 12   # 1px pad inside the 10px zone starting at y=11
DIVIDER1_Y    = 10
DIVIDER2_Y    = 21
COUNTDOWN_Y   = 23   # 1px pad inside the 10px zone starting at y=22


def _ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _days_until_season():
    delta = (SEASON_START - datetime.date.today()).days
    return max(delta, 0)


def _text_w(draw, text, font):
    try:
        return int(draw.textlength(text, font=font))
    except Exception:
        return len(text) * 5   # 5x8 fallback estimate


class OffseasonScreen:
    """One instance per league quadrant. Holds its own scroll state."""

    W = 32
    H = 32

    def __init__(self, league, config):
        self.league = league
        self.config = config
        self._fn = fonts.font_5x8()
        self._hl = tuple(config["display"]["highlight_color"])

        # Measure league name width for scroll range
        name = league.name or "League"
        tmp = Image.new("RGB", (500, 12))
        self._name_w = _text_w(ImageDraw.Draw(tmp), name, self._fn)
        # scroll: 0 = name just offscreen right; wraps after full pass + pause
        self._scroll_range = self.W + self._name_w + SCROLL_PAUSE_FRAMES
        self._scroll_offset = 0

    # ------------------------------------------------------------------
    def tick(self):
        self._scroll_offset = (self._scroll_offset + SCROLL_SPEED) % self._scroll_range

    # ------------------------------------------------------------------
    def _my_rank(self):
        for i, roster in enumerate(self.league.standings):
            if roster.get("roster_id") == self.league.roster_id:
                return i + 1
        return None

    # ------------------------------------------------------------------
    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.W, self.H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        fn = self._fn

        # ── Scrolling league name (clipped to top NAME_STRIP_H px) ────────
        name_strip = Image.new("RGB", (self.W, NAME_STRIP_H), (0, 0, 0))
        strip_draw = ImageDraw.Draw(name_strip)
        strip_draw.text(
            (self.W - self._scroll_offset, 1),
            self.league.name or "League",
            font=fn,
            fill=(0, 200, 255),
        )
        img.paste(name_strip, (0, 0))

        # ── Dividers ──────────────────────────────────────────────────────
        draw.line([(0, DIVIDER1_Y), (31, DIVIDER1_Y)], fill=(45, 45, 45))
        draw.line([(0, DIVIDER2_Y), (31, DIVIDER2_Y)], fill=(45, 45, 45))

        # ── Rank ordinal (centered, no "place") ───────────────────────────
        rank = self._my_rank()
        rank_str = _ordinal(rank) if rank else "?"
        rw = _text_w(draw, rank_str, fn)
        draw.text(((self.W - rw) // 2, RANK_Y), rank_str, font=fn, fill=self._hl)

        # ── Countdown ─────────────────────────────────────────────────────
        days = _days_until_season()
        cd_str = f"{days}d" if days > 0 else "Soon!"
        cw = _text_w(draw, cd_str, fn)
        draw.text(((self.W - cw) // 2, COUNTDOWN_Y), cd_str,
                  font=fn, fill=(255, 200, 0))

        return img
