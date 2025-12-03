# import os
# import requests
# import pandas as pd
# from datetime import datetime

# API_KEY = open("api_key.txt").read().strip()

# BASE_URL = "https://v3.football.api-sports.io"
# HEADERS = {"x-apisports-key": API_KEY}

# LEAGUES = {
#     "Premier League": 39,
#     "La Liga": 140,
#     "Bundesliga": 78,
#     "Serie A": 135,
#     "Ligue 1": 61
# }

# START_DATE = "2025-05-25"


# END_DATE = "2025-12-31"

# SEASONS = [2024, 2025] 

# # Output CSV file
# OUTPUT_CSV = "upcoming_matches_from_2025-05-25.csv"


# def fetch_fixtures_for_league_season(league_name: str, league_id: int, season: int) -> pd.DataFrame:

#     url = f"{BASE_URL}/fixtures"
#     params = {
#         "league": league_id,
#         "season": season,
#         "from": START_DATE,
#         "to": END_DATE,
#     }
#     headers = {
#         "x-apisports-key": API_KEY,
#         "Accept": "application/json",
#     }

#     print(f"Fetching fixtures for {league_name} (ID {league_id}), season {season}, from {START_DATE} to {END_DATE}...")

#     r = requests.get(url, params=params, headers=headers, timeout=30)
#     r.raise_for_status()
#     data = r.json()

#     # API-Football wraps data under "response"
#     fixtures = data.get("response", [])

#     print(f"  -> got {len(fixtures)} fixtures")

#     rows = []
#     for item in fixtures:
#         fixture = item.get("fixture", {})
#         league_info = item.get("league", {})
#         teams = item.get("teams", {})
#         goals = item.get("goals", {})
#         date_str = fixture.get("date")
#         row = {
#             "fixture_id": fixture.get("id"),
#             "league": league_info.get("name"),
#             "season": league_info.get("season"),
#             "date": date_str,
#             "home_team": teams.get("home", {}).get("name"),
#             "away_team": teams.get("away", {}).get("name"),
#             "home_goals": goals.get("home"),  # will be None for future fixtures
#             "away_goals": goals.get("away"),
#             # placeholders for your model predictions (to be filled later)
#             "prob_home_win": None,
#             "prob_draw": None,
#             "prob_away_win": None,
#         }
#         rows.append(row)

#     if not rows:
#         return pd.DataFrame()

#     return pd.DataFrame(rows)


# def main():
#     all_dfs = []

#     for league_name, league_id in LEAGUE_IDS.items():
#         for season in SEASONS:
#             df_league_season = fetch_fixtures_for_league_season(
#                 league_name=league_name,
#                 league_id=league_id,
#                 season=season,
#             )
#             if not df_league_season.empty:
#                 all_dfs.append(df_league_season)

#     if not all_dfs:
#         print("No fixtures found for the given leagues/seasons/date range.")
#         return

#     combined = pd.concat(all_dfs, ignore_index=True)

#     # Optional: remove duplicates by fixture_id if you run script multiple times
#     combined.drop_duplicates(subset=["fixture_id"], inplace=True)

#     # Sort by date
#     combined["date"] = pd.to_datetime(combined["date"], errors="coerce", utc=True)
#     combined.sort_values(["league", "season", "date"], inplace=True)

#     # Save to CSV
#     combined.to_csv(OUTPUT_CSV, index=False)
#     print(f"Saved {len(combined)} upcoming fixtures to {OUTPUT_CSV}")


# if __name__ == "__main__":
#     main()
