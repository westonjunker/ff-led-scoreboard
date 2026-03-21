"""Standings screen — league standings."""


class StandingsScreen:
    def __init__(self, league, state, config):
        self.league = league
        self.state = state
        self.config = config

    def render(self):
        print(f"[standings] {self.league.name}")
        # TODO: fetch and render roster standings
