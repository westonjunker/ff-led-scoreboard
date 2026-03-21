"""Pillow → matrix frame rendering base utilities."""

from PIL import Image, ImageDraw, ImageFont


class Renderer:
    def __init__(self, config):
        panels = config["panels"]
        self.width = panels["cols"]
        self.height = panels["rows"] * panels["parallel"]
        self.highlight_color = tuple(config["display"]["highlight_color"])
        self.dim_color = tuple(config["display"]["dim_color"])

    def new_image(self):
        return Image.new("RGB", (self.width, self.height), (0, 0, 0))

    def draw(self, image):
        return ImageDraw.Draw(image)

    def render_to_matrix(self, matrix, image):
        """Push a Pillow image to the LED matrix."""
        matrix.SetImage(image.convert("RGB"))
