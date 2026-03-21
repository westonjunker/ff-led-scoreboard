"""Header screen — league name and current week."""

from PIL import Image, ImageDraw
import fonts

W, H = 32, 32


class HeaderScreen:
    def __init__(self, league, config):
        self.league = league
        self.highlight = tuple(config["display"]["highlight_color"])
        self.dim = tuple(config["display"]["dim_color"])

    def render(self) -> Image.Image:
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        f = fonts.font_5x8()

        # Truncate to 6 chars to fit 32px width at 5px per char
        name = self.league.name[:6]
        draw.text((1, 7),  name, fill=self.highlight, font=f)
        draw.text((1, 18), f"Wk{self.league.week}", fill=self.dim, font=f)

        return img
