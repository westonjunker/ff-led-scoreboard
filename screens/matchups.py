"""Matchup screen — my matchup only."""


class MatchupScreen:
    def __init__(self, league, state, config):
        self.league = league
        self.state = state
        self.config = config

    def render(self):
        my = self.league.my_matchup
        opp = self.league.opponent_matchup
        my_pts = my["points"] if my else "?"
        opp_pts = opp["points"] if opp else "?"
        print(f"[matchup] ▶ {my_pts}  vs  {opp_pts}")
        # TODO: render to matrix via renderer
