"""Matchup screen — my score vs opponent."""

from PIL import Image, ImageDraw, ImageFont

W, H = 32, 32


class MatchupScreen:
    def __init__(self, league, config):
        self.league = league
        self.highlight = tuple(config["display"]["highlight_color"])
        self.dim = tuple(config["display"]["dim_color"])

    def render(self) -> Image.Image:
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        my = self.league.my_matchup
        opp = self.league.opponent_matchup

        my_pts = f"{my['points']:.1f}" if my and my.get("points") is not None else "--"
        opp_pts = f"{opp['points']:.1f}" if opp and opp.get("points") is not None else "--"

        # ▶ marker next to my score
        draw.text((2, 6),  f"\u25b6{my_pts}", fill=self.highlight, font=font)
        draw.text((2, 18), f" {opp_pts}", fill=self.dim, font=font)

        return img
