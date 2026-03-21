"""Entry point — all four leagues displayed simultaneously in quadrants."""

import platform
import time
import yaml
from PIL import Image

from sleeper_client import SleeperClient, SleeperOfflineError
from state import State
from screens.header import HeaderScreen
from screens.matchups import MatchupScreen
from screens.standings import StandingsScreen

# Quadrant positions (x, y) for up to 4 leagues
QUADRANT_POSITIONS = [(0, 0), (32, 0), (0, 32), (32, 32)]

SCREEN_SEQUENCE = [
    (HeaderScreen,   2),
    (MatchupScreen,  6),
    (StandingsScreen, 5),
]


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def make_matrix(config):
    p = config["panels"]
    is_pi = platform.system() == "Linux" and platform.machine().startswith("arm")
    if is_pi:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
        options = RGBMatrixOptions()
        options.rows = p["rows"]
        options.cols = p["cols"]
        options.chain_length = p["chain_length"]
        options.parallel = p["parallel"]
        options.brightness = config["display"]["brightness"]
        options.hardware_mapping = "adafruit-hat"
        return RGBMatrix(options=options)
    else:
        from mock_matrix import MockMatrix
        return MockMatrix(rows=p["rows"] * p["parallel"], cols=p["cols"])


def compose(league_images, total_w=64, total_h=64):
    """Paste up to 4 league frames into quadrants on a single canvas."""
    canvas = Image.new("RGB", (total_w, total_h), (0, 0, 0))
    for img, pos in zip(league_images, QUADRANT_POSITIONS):
        canvas.paste(img, pos)
    # Draw 1px dividers between quadrants
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    draw.line([(31, 0), (31, total_h - 1)], fill=(30, 30, 30))   # vertical
    draw.line([(0, 31), (total_w - 1, 31)], fill=(30, 30, 30))   # horizontal
    return canvas


def offline_frame():
    img = Image.new("RGB", (32, 32), (0, 0, 0))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((2, 10), "No", fill=(180, 40, 40), font=font)
    draw.text((2, 20), "signal", fill=(180, 40, 40), font=font)
    return img


def main():
    config = load_config()
    matrix = make_matrix(config)
    client = SleeperClient(config)
    state = State(client, config)

    while True:
        try:
            state.refresh()
        except SleeperOfflineError as e:
            print(f"[main] Offline: {e}")

        if state.offline or not state.leagues:
            canvas = compose([offline_frame()] * 4)
            matrix.SetImage(canvas)
            time.sleep(10)
            continue

        for ScreenClass, duration in SCREEN_SEQUENCE:
            # Collect frames per league — render() returns Image or list of Images
            all_frames = []
            for league in state.leagues[:4]:
                result = ScreenClass(league, config).render()
                all_frames.append(result if isinstance(result, list) else [result])

            # Pad to 4 quadrants
            while len(all_frames) < 4:
                all_frames.append([Image.new("RGB", (32, 32), (0, 0, 0))])

            max_pages = max(len(f) for f in all_frames)
            page_duration = duration / max_pages

            for page in range(max_pages):
                images = [f[min(page, len(f) - 1)] for f in all_frames]
                matrix.SetImage(compose(images))
                time.sleep(page_duration)


if __name__ == "__main__":
    main()
