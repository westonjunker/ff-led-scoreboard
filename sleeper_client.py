"""Sleeper API client — full resolution chain and data fetching."""

import requests

BASE_URL = "https://api.sleeper.app/v1"
TIMEOUT = 10
MAX_RETRIES = 3


class SleeperOfflineError(Exception):
    """Raised when the Sleeper API is unreachable."""


class SleeperClient:
    def __init__(self, config):
        self.username = config["sleeper"]["username"]
        self.season = config["sleeper"]["season"]
        self._user_id = None
        # Cache roster_id per league so we don't re-fetch rosters every cycle
        self._roster_id_cache = {}

    # ------------------------------------------------------------------
    # Core HTTP
    # ------------------------------------------------------------------

    def _get(self, path):
        """GET with retry logic. Raises SleeperOfflineError if unreachable."""
        url = f"{BASE_URL}{path}"
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                last_exc = e
            except requests.exceptions.Timeout as e:
                last_exc = e
            except requests.exceptions.HTTPError as e:
                # 4xx errors won't recover on retry
                raise SleeperOfflineError(f"HTTP error on {path}: {e}") from e
        raise SleeperOfflineError(
            f"Could not reach Sleeper API after {MAX_RETRIES} attempts: {last_exc}"
        )

    # ------------------------------------------------------------------
    # Resolution chain: username → user_id → leagues → roster_id → matchups
    # ------------------------------------------------------------------

    def get_user_id(self):
        """Step 1: resolve username → user_id (cached after first call)."""
        if not self._user_id:
            data = self._get(f"/user/{self.username}")
            if not data or "user_id" not in data:
                raise SleeperOfflineError(
                    f"User '{self.username}' not found on Sleeper."
                )
            self._user_id = data["user_id"]
        return self._user_id

    def get_leagues(self):
        """Step 2: fetch all NFL leagues for this user in the configured season."""
        user_id = self.get_user_id()
        leagues = self._get(f"/user/{user_id}/leagues/nfl/{self.season}")
        if not leagues:
            return []
        return leagues

    def get_rosters(self, league_id):
        """Step 3 (helper): fetch all rosters for a league."""
        return self._get(f"/league/{league_id}/rosters") or []

    def get_roster_id(self, league_id):
        """Step 3: find this user's roster_id within a league (cached)."""
        if league_id in self._roster_id_cache:
            return self._roster_id_cache[league_id]

        user_id = self.get_user_id()
        rosters = self.get_rosters(league_id)
        for roster in rosters:
            if roster.get("owner_id") == user_id:
                self._roster_id_cache[league_id] = roster["roster_id"]
                return roster["roster_id"]

        # Co-managed or orphaned roster fallback — should not happen normally
        raise SleeperOfflineError(
            f"No roster found for user '{self.username}' in league {league_id}."
        )

    def get_matchups(self, league_id, week):
        """Step 4: fetch all matchup data for a league/week."""
        return self._get(f"/league/{league_id}/matchups/{week}") or []

    def get_nfl_state(self):
        """Step 5: fetch current NFL week and season state."""
        return self._get("/state/nfl")

    # ------------------------------------------------------------------
    # Convenience: resolve everything for one refresh cycle
    # ------------------------------------------------------------------

    def resolve_all(self):
        """
        Full resolution pass. Returns a tuple of:
            (nfl_state, [(league_data, roster_id, matchups), ...])
        Raises SleeperOfflineError if any step fails.
        """
        nfl_state = self.get_nfl_state()
        week = nfl_state.get("week", 1)

        leagues = self.get_leagues()
        resolved = []
        for league_data in leagues:
            league_id = league_data["league_id"]
            roster_id = self.get_roster_id(league_id)
            matchups = self.get_matchups(league_id, week)
            resolved.append((league_data, roster_id, matchups))

        return nfl_state, resolved
