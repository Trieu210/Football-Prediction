import requests
import pandas as pd
from pathlib import Path

API_KEY = open("api_key.txt").read().strip()

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Bundesliga": 78,
    "Serie A": 135,
    "Ligue 1": 61
}

OUTPUT_DIR = Path("data_api_football")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_league_seasons(league_id):
    """Return available seasons for this league"""
    url = f"{BASE_URL}/leagues"
    params = {"id": league_id}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)

    if resp.status_code != 200:
        print(f"[ERROR] League {league_id} season call:", resp.text[:200])
        return []

    data = resp.json().get("response", [])
    if not data:
        print(f"[WARNING] No seasons found for league {league_id}")
        return []

    seasons = [item["year"] for item in data[0].get("seasons", [])]
    seasons = sorted(seasons)
    print(f"League {league_id} seasons: {seasons}")
    return seasons


def get_matches(league_code, league_id, seasons):
    """Fetch all fixtures for the given league & list of seasons"""
    rows = []

    for season in seasons:
        print(f"\nFetching matches for {league_code} season {season}...")
        url = f"{BASE_URL}/fixtures"
        params = {"league": league_id, "season": season}

        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)

        if resp.status_code != 200:
            print(f"  [ERROR] {resp.status_code}: {resp.text[:200]}")
            continue

        matches = resp.json().get("response", [])
        print(f"  Retrieved {len(matches)} matches.")

        for m in matches:
            fixture = m.get("fixture", {})
            teams = m.get("teams", {})
            goals = m.get("goals", {})

            rows.append({
                "league": league_code,
                "season": season,
                "fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "home_team": teams.get("home", {}).get("name"),
                "away_team": teams.get("away", {}).get("name"),
                "home_goals": goals.get("home"),
                "away_goals": goals.get("away")
            })

    return rows


def main():
    all_rows = []

    for code, league_id in LEAGUES.items():
        print(f"\n=== Getting seasons for {code} ({league_id}) ===")
        seasons = get_league_seasons(league_id)

        if len(seasons) == 0:
            continue

        # LAST 5 seasons only
        last5 = seasons[-5:]
        print(f"Using seasons: {last5}")

        rows = get_matches(code, league_id, last5)
        all_rows.extend(rows)

    if not all_rows:
        print("No data fetched.")
        return

    df = pd.DataFrame(all_rows)
    out_file = OUTPUT_DIR / "All_matches_2018-2025.csv"
    df.to_csv(out_file, index=False)

    print("\n================================================")
    print("DONE! Saved:", out_file)
    print("Total matches:", len(df))


if __name__ == "__main__":
    main()
