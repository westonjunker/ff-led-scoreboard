"""Header screen — league name and current week."""

from PIL import Image, ImageDraw, ImageFont

W, H = 32, 32


class HeaderScreen:
    def __init__(self, league, config):
        self.league = league
        self.highlight = tuple(config["display"]["highlight_color"])
        self.dim = tuple(config["display"]["dim_color"])

    def render(self) -> Image.Image:
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        # Truncate league name to ~5 chars to fit 32px width
        name = self.league.name[:5]
        draw.text((2, 8), name, fill=self.highlight, font=font)
        draw.text((2, 20), f"Wk{self.league.week}", fill=self.dim, font=font)

        return img
