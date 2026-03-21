"""Standings screen — win/loss records, paged to show all teams."""

from PIL import Image, ImageDraw
import fonts

W, H = 32, 32
PAGE_SIZE = 4  # rows visible at once (4x6 font, 7px per row)


class StandingsScreen:
    def __init__(self, league, config):
        self.league = league
        self.highlight = tuple(config["display"]["highlight_color"])
        self.dim = tuple(config["display"]["dim_color"])

    def render(self) -> list:
        """Return one Image per page of standings."""
        standings = self.league.standings
        pages = []
        for start in range(0, len(standings), PAGE_SIZE):
            chunk = standings[start:start + PAGE_SIZE]
            pages.append(self._render_page(chunk, start))
        return pages or [Image.new("RGB", (W, H), (0, 0, 0))]

    def _render_page(self, chunk, start_rank):
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        f = fonts.font_4x6()
        y = 2
        for i, roster in enumerate(chunk):
            s = roster.get("settings") or {}
            wins   = s.get("wins", 0)
            losses = s.get("losses", 0)
            is_me  = roster["roster_id"] == self.league.roster_id
            marker = ">" if is_me else " "
            color  = self.highlight if is_me else self.dim
            draw.text((1, y), f"{marker}{wins}-{losses}", fill=color, font=f)
            y += 7
        return img
