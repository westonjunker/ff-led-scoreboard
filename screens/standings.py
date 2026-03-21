"""Standings screen — top entries by points scored."""

from PIL import Image, ImageDraw, ImageFont

W, H = 32, 32


class StandingsScreen:
    def __init__(self, league, config):
        self.league = league
        self.highlight = tuple(config["display"]["highlight_color"])
        self.dim = tuple(config["display"]["dim_color"])

    def render(self) -> Image.Image:
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        sorted_matchups = sorted(
            self.league.matchups,
            key=lambda m: m.get("points") or 0,
            reverse=True,
        )

        y = 2
        for i, m in enumerate(sorted_matchups[:3]):
            pts = f"{m['points']:.0f}" if m.get("points") is not None else "--"
            marker = "\u25b6" if m["roster_id"] == self.league.roster_id else " "
            color = self.highlight if m["roster_id"] == self.league.roster_id else self.dim
            draw.text((2, y), f"{marker}{i+1}.{pts}", fill=color, font=font)
            y += 10

        return img
