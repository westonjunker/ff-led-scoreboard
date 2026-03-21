"""Cached scores, current week, roster IDs, and league state."""

from sleeper_client import SleeperOfflineError


class LeagueState:
    def __init__(self, league_data, roster_id, matchups, week):
        self.league_id = league_data["league_id"]
        self.name = league_data["name"]
        self.roster_id = roster_id
        self.matchups = matchups
        self.week = week

    @property
    def my_matchup(self):
        for m in self.matchups:
            if m["roster_id"] == self.roster_id:
                return m
        return None

    @property
    def opponent_matchup(self):
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
        self.offline = False

    def refresh(self):
        try:
            nfl_state, resolved = self.client.resolve_all()
            self.current_week = nfl_state.get("week", 1)
            self.offline = False
            self.leagues = [
                LeagueState(league_data, roster_id, matchups, self.current_week)
                for league_data, roster_id, matchups in resolved
            ]
        except SleeperOfflineError as e:
            print(f"[state] Offline: {e}")
            self.offline = True
            # Retain stale league data so the display doesn't go blank
