"""Sleeper API client — full resolution chain and data fetching."""

import requests

BASE_URL = "https://api.sleeper.app/v1"


class SleeperClient:
    def __init__(self, config):
        self.username = config["sleeper"]["username"]
        self.season = config["sleeper"]["season"]
        self._user_id = None

    def _get(self, path):
        """GET request with basic error handling."""
        url = f"{BASE_URL}{path}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_user_id(self):
        if not self._user_id:
            data = self._get(f"/user/{self.username}")
            self._user_id = data["user_id"]
        return self._user_id

    def get_leagues(self):
        user_id = self.get_user_id()
        return self._get(f"/user/{user_id}/leagues/nfl/{self.season}")

    def get_rosters(self, league_id):
        return self._get(f"/league/{league_id}/rosters")

    def get_matchups(self, league_id, week):
        return self._get(f"/league/{league_id}/matchups/{week}")

    def get_nfl_state(self):
        return self._get("/state/nfl")

    def get_roster_id(self, league_id):
        """Find this user's roster_id within a league."""
        user_id = self.get_user_id()
        rosters = self.get_rosters(league_id)
        for roster in rosters:
            if roster["owner_id"] == user_id:
                return roster["roster_id"]
        return None
