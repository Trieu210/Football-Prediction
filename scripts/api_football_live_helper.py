import requests
BASE_URL = "https://v3.football.api-sports.io"

# Get live fixtures
def get_live_fixtures(headers, timeout=25):
    url = f"{BASE_URL}/fixtures"
    r = requests.get(url, headers=headers, params = {"live":"all"},timeout=timeout)
    r.raise_for_status()
    data = r.json().get("response", []) or []
    print("API /fixtures?live=all returned:", len(data), "fixtures")
    return data

# Get fixtures by league and season
def get_fixtures_by_league_season(headers, league_id, season, timeout=25):
    url = f"{BASE_URL}/fixtures"
    r = requests.get(
        url,
        headers=headers,
        params={"league": league_id, "season": season},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json().get("response", []) or []

# Get fixture statistics
def get_fixture_event(headers, fixture_id, timeout=20):
    url = f"{BASE_URL}/fixtures/events"
    r = requests.get(url, headers=headers, params={"fixture": fixture_id}, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response", []) or []

# Get fixture lineups
def getfixture_lineups(headers, fixture_id, timeout=20):
    url = f"{BASE_URL}/fixtures/lineups"
    r = requests.get(url, headers=headers, params={"fixture": fixture_id}, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response", []) or []

# Get head-to-head fixtures between two teams
def get_head_to_head(headers, team1_id, team2_id, league=None, season=None, last=10, timeout=25):
    url = f"{BASE_URL}/fixtures/headtohead"
    params = {"h2h": f"{team1_id}-{team2_id}", "last": last}
    if league: params["league"] = league
    if season: params["season"] = season

    r = requests.get(url, headers=headers, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response", []) or []
