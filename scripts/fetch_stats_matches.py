import time
import requests
import pandas as pd
from pathlib import Path

API_KEY = open("api_key.txt").read().strip()

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

INPUT_CSV = Path("data_api_football") / "All_matches_2018-2025.csv"
OUTPUT_CSV = Path("data_api_football") / "All_matches_2018-2025_with_stats.csv"


def extract_stat(stats_list, stat_name):
    """Find a stat in API-Football statistics list by its 'type'."""
    for s in stats_list:
        if s.get("type") == stat_name:
            val = s.get("value")
            if val is None:
                return None
            if isinstance(val, str) and val.endswith("%"):
                try:
                    return float(val.strip("%"))
                except ValueError:
                    return None
            try:
                return float(val)
            except (TypeError, ValueError):
                return None
    return None


def fetch_fixture_stats(fixture_id, home_team_name, away_team_name):
    """Fetch stats for one fixture, return dict of home/away metrics."""
    url = f"{BASE_URL}/fixtures/statistics"
    params = {"fixture": fixture_id}

    resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
    if resp.status_code != 200:
        print(f"[{fixture_id}] stats error {resp.status_code}: {resp.text[:200]}")
        return {}

    data = resp.json().get("response", [])
    if not data:
        print(f"[{fixture_id}] no stats in response")
        return {}

    home_stats = {}
    away_stats = {}

    # there are usually two entries: one per team
    for entry in data:
        team = entry.get("team", {}) or {}
        name = team.get("name")
        stats = entry.get("statistics", []) or []

        # match by team name vs our CSV
        if name == home_team_name:
            home_stats = {
                "home_shots_total": extract_stat(stats, "Total Shots"),
                "home_shots_inbox": extract_stat(stats, "Shots insidebox"),
                "home_possession": extract_stat(stats, "Ball Possession"),
                "home_pass_accuracy": extract_stat(stats, "Passes %"),
                "home_corners": extract_stat(stats, "Corner Kicks"),
                "home_fouls": extract_stat(stats, "Fouls"),
            }
        elif name == away_team_name:
            away_stats = {
                "away_shots_total": extract_stat(stats, "Total Shots"),
                "away_shots_inbox": extract_stat(stats, "Shots insidebox"),
                "away_possession": extract_stat(stats, "Ball Possession"),
                "away_pass_accuracy": extract_stat(stats, "Passes %"),
                "away_corners": extract_stat(stats, "Corner Kicks"),
                "away_fouls": extract_stat(stats, "Fouls"),
            }

    # if names don't match exactly for some reason, just leave missing
    combined = {}
    combined.update(home_stats)
    combined.update(away_stats)
    return combined


def main():
    df = pd.read_csv(INPUT_CSV)
    print("Loaded matches:", len(df))

    rows = []
    total = len(df)

    for i, row in df.iterrows():
        fixture_id = int(row["fixture_id"])
        home_team = row["home_team"]
        away_team = row["away_team"]

        print(f"[{i+1}/{total}] fixture={fixture_id} {home_team} vs {away_team}")
        stats = fetch_fixture_stats(fixture_id, home_team, away_team)

        out_row = row.to_dict()
        out_row.update(stats)
        rows.append(out_row)

        # be a bit gentle to avoid hitting limits hard
        time.sleep(0.15)

    out_df = pd.DataFrame(rows)
    print("Final rows:", len(out_df))
    out_df.to_csv(OUTPUT_CSV, index=False)
    print("Saved with stats to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
