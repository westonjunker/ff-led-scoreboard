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
from screens.offseason import OffseasonScreen

# Quadrant positions (x, y) for up to 4 leagues
QUADRANT_POSITIONS = [(0, 0), (32, 0), (0, 32), (32, 32)]

SCREEN_SEQUENCE_LIVE = [
    (HeaderScreen,    2),
    (MatchupScreen,   6),
    (StandingsScreen, 5),
]

OFFSEASON_FPS        = 20          # frames per second for scroll animation
OFFSEASON_REFRESH_S  = 300         # re-poll Sleeper every 5 minutes


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def make_matrix(config):
    p = config["panels"]
    is_pi = platform.system() == "Linux" and platform.machine().startswith(("arm", "aarch"))
    if is_pi:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
        options = RGBMatrixOptions()
        options.rows = p["rows"]
        options.cols = p["cols"]
        options.chain_length = p["chain_length"]
        options.parallel = p["parallel"]
        options.brightness = config["display"]["brightness"]
        options.hardware_mapping = "adafruit-hat"
        if p.get("pixel_mapper"):
            options.pixel_mapper_config = p["pixel_mapper"]
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
    # Bottom panel (y=32-63) scans in reverse due to chain wiring —
    # pre-rotate 180° so the hardware inversion cancels out.
    bottom = canvas.crop((0, 32, total_w, total_h)).rotate(180)
    canvas.paste(bottom, (0, 32))
    return canvas


def offline_frame():
    img = Image.new("RGB", (32, 32), (0, 0, 0))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((2, 10), "No", fill=(180, 40, 40), font=font)
    draw.text((2, 20), "signal", fill=(180, 40, 40), font=font)
    return img


def _build_offseason_screens(state, config):
    screens = [OffseasonScreen(l, config) for l in state.leagues[:4]]
    while len(screens) < 4:
        screens.append(None)
    return screens


def run_offseason(matrix, state, config):
    """Scrolling offseason animation. Returns when live season is detected."""
    print("[main] Offseason mode — starting scroll animation")
    screens = _build_offseason_screens(state, config)
    last_refresh = time.time()
    frame_delay = 1.0 / OFFSEASON_FPS

    while True:
        frames = [
            s.render() if s else Image.new("RGB", (32, 32), (0, 0, 0))
            for s in screens
        ]
        matrix.SetImage(compose(frames))
        for s in screens:
            if s:
                s.tick()
        time.sleep(frame_delay)

        # Periodically refresh — break out if season has started
        if time.time() - last_refresh > OFFSEASON_REFRESH_S:
            try:
                state.refresh()
            except SleeperOfflineError:
                pass
            last_refresh = time.time()
            if state.season_has_scores:
                print("[main] Season started — switching to live mode")
                return
            screens = _build_offseason_screens(state, config)


def run_live(matrix, state, config):
    """One full rotation through all live screens, then returns."""
    for ScreenClass, duration in SCREEN_SEQUENCE_LIVE:
        all_frames = []
        for league in state.leagues[:4]:
            result = ScreenClass(league, config).render()
            all_frames.append(result if isinstance(result, list) else [result])

        while len(all_frames) < 4:
            all_frames.append([Image.new("RGB", (32, 32), (0, 0, 0))])

        max_pages = max(len(f) for f in all_frames)
        page_duration = duration / max_pages

        for page in range(max_pages):
            images = [f[min(page, len(f) - 1)] for f in all_frames]
            matrix.SetImage(compose(images))
            time.sleep(page_duration)


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
            matrix.SetImage(compose([offline_frame()] * 4))
            time.sleep(10)
            continue

        if not state.season_has_scores:
            run_offseason(matrix, state, config)
        else:
            run_live(matrix, state, config)


if __name__ == "__main__":
    main()
