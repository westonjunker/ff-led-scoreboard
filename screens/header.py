"""Header screen — league name and current week."""


class HeaderScreen:
    def __init__(self, league, state, config):
        self.league = league
        self.state = state
        self.config = config

    def render(self):
        print(f"[header] {self.league.name} — Week {self.league.week}")
        # TODO: render to matrix via renderer
