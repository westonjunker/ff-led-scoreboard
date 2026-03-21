"""Standings screen — win/loss records sorted by wins then points-for."""

from PIL import Image, ImageDraw
import fonts

W, H = 32, 32


class StandingsScreen:
    def __init__(self, league, config):
        self.league = league
        self.highlight = tuple(config["display"]["highlight_color"])
        self.dim = tuple(config["display"]["dim_color"])

    def render(self) -> Image.Image:
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        f = fonts.font_4x6()

        y = 2
        for roster in self.league.standings[:4]:
            s = roster.get("settings") or {}
            wins   = s.get("wins", 0)
            losses = s.get("losses", 0)
            is_me  = roster["roster_id"] == self.league.roster_id
            marker = ">" if is_me else " "
            color  = self.highlight if is_me else self.dim
            draw.text((1, y), f"{marker}{wins}-{losses}", fill=color, font=f)
            y += 7  # 6px glyph + 1px gap

        return img
