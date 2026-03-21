"""Entry point — rotation loop across leagues and screens."""

import time
import yaml
from sleeper_client import SleeperClient
from state import State
from screens.header import HeaderScreen
from screens.matchups import MatchupScreen
from screens.standings import StandingsScreen


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    client = SleeperClient(config)
    state = State(client, config)

    screens_per_league = [HeaderScreen, MatchupScreen, StandingsScreen]
    rotation_seconds = config["display"]["rotation_seconds"]

    while True:
        state.refresh()
        for league in state.leagues:
            for ScreenClass in screens_per_league:
                screen = ScreenClass(league, state, config)
                screen.render()
                time.sleep(rotation_seconds)


if __name__ == "__main__":
    main()
