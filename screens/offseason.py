"""Offseason display: scrolling league name, final finish position, countdown to kickoff."""

import datetime
from PIL import Image, ImageDraw
import fonts

SEASON_START = datetime.date(2026, 9, 4)
SCROLL_SPEED = 1          # px per tick
SCROLL_PAUSE_FRAMES = 60  # blank frames between scroll cycles (~3s at 20fps)


def _ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _days_until_season():
    delta = (SEASON_START - datetime.date.today()).days
    return max(delta, 0)


class OffseasonScreen:
    """One instance per league quadrant. Holds its own scroll state."""

    W = 32
    H = 32

    def __init__(self, league, config):
        self.league = league
        self.config = config
        self._fn = fonts.font_4x6()
        self._hl = tuple(config["display"]["highlight_color"])
        self._dim = tuple(config["display"]["dim_color"])

        name = league.name or "League"
        # Measure approximate text width (4px/char is a safe default for 4x6)
        try:
            tmp = Image.new("RGB", (500, 10))
            tw = int(ImageDraw.Draw(tmp).textlength(name, font=self._fn))
        except Exception:
            tw = len(name) * 4
        self._name_w = max(tw, len(name) * 4)
        # scroll goes from 0 → W + name_w + pause, then wraps
        self._scroll_range = self.W + self._name_w + SCROLL_PAUSE_FRAMES
        self._scroll_offset = 0  # start: name just off the right edge

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

        # ── Scrolling league name (clipped to top 7px) ─────────────────
        name_strip = Image.new("RGB", (self.W, 7), (0, 0, 0))
        strip_draw = ImageDraw.Draw(name_strip)
        x = self.W - self._scroll_offset
        strip_draw.text((x, 0), self.league.name or "League",
                        font=fn, fill=(0, 200, 255))
        img.paste(name_strip, (0, 0))

        # ── Divider ─────────────────────────────────────────────────────
        draw.line([(0, 8), (31, 8)], fill=(45, 45, 45))

        # ── Finish position ─────────────────────────────────────────────
        rank = self._my_rank()
        rank_str = _ordinal(rank) if rank else "?"

        try:
            rw = int(draw.textlength(rank_str, font=fn))
        except Exception:
            rw = len(rank_str) * 4
        draw.text(((self.W - rw) // 2, 10), rank_str, font=fn, fill=self._hl)

        try:
            pw = int(draw.textlength("place", font=fn))
        except Exception:
            pw = 20
        draw.text(((self.W - pw) // 2, 17), "place", font=fn, fill=self._dim)

        # ── Divider ─────────────────────────────────────────────────────
        draw.line([(0, 24), (31, 24)], fill=(45, 45, 45))

        # ── Countdown ───────────────────────────────────────────────────
        days = _days_until_season()
        cd_str = f"{days}d" if days > 0 else "Soon!"
        try:
            cw = int(draw.textlength(cd_str, font=fn))
        except Exception:
            cw = len(cd_str) * 4
        draw.text(((self.W - cw) // 2, 26), cd_str,
                  font=fn, fill=(255, 200, 0))

        return img
