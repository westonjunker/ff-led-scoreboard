"""Cached scores, current week, roster IDs, and league state."""


class LeagueState:
    def __init__(self, league_data, roster_id, matchups, week):
        self.league_id = league_data["league_id"]
        self.name = league_data["name"]
        self.roster_id = roster_id
        self.matchups = matchups
        self.week = week

    @property
    def my_matchup(self):
        """Return the matchup dict for this user's roster."""
        for m in self.matchups:
            if m["roster_id"] == self.roster_id:
                return m
        return None

    @property
    def opponent_matchup(self):
        """Return the opponent's matchup dict."""
        my = self.my_matchup
        if not my:
            return None
        matchup_id = my["matchup_id"]
        for m in self.matchups:
            if m["matchup_id"] == matchup_id and m["roster_id"] != self.roster_id:
                return m
        return None


class State:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.leagues = []
        self.current_week = None
        self.season = config["sleeper"]["season"]

    def refresh(self):
        try:
            nfl_state = self.client.get_nfl_state()
            self.current_week = nfl_state.get("week", 1)

            raw_leagues = self.client.get_leagues()
            self.leagues = []

            for league_data in raw_leagues:
                league_id = league_data["league_id"]
                roster_id = self.client.get_roster_id(league_id)
                matchups = self.client.get_matchups(league_id, self.current_week)
                self.leagues.append(
                    LeagueState(league_data, roster_id, matchups, self.current_week)
                )
        except Exception as e:
            print(f"[state] Refresh error: {e}")
