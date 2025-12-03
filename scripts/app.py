from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # allow React dev server to call this API
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) # enable CORS for all /api/* endpoints

DATA_DIR = Path("data_api_football")
MATCHES_CSV = DATA_DIR / "matches_with_probs.csv"

# Existing df for finished matches (with probabilities)
print("Loading matches from:", MATCHES_CSV)
df = pd.read_csv(MATCHES_CSV)
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)

STATS_CSV = DATA_DIR / "All_matches_2018-2025_with_stats_and_prematch_probs.csv"
print("Loading upcoming matches from:", STATS_CSV)
df_stats = pd.read_csv(STATS_CSV)
df_stats["date"] = pd.to_datetime(df_stats["date"], errors="coerce", utc=True)

@app.route("/")
def health():
    return "Backend is running. Use GET /api/matches"


@app.route("/api/matches")
def get_matches():

    limit = int(request.args.get("limit", 100))
    league = request.args.get("league")
    season = request.args.get("season")

    filtered = df.copy()

    if league:
        filtered = filtered[filtered["league"] == league]

    if season:
        # season may be int in df, string in query
        filtered = filtered[filtered["season"].astype(str) == str(season)]

    # sort by date if available
    if "date" in filtered.columns:
        filtered = filtered.sort_values("date", ascending=False)

    filtered = filtered.head(limit)

    cols_to_send = [
        "fixture_id",
        "league",
        "season",
        "date",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
        "prob_away_win",
        "prob_draw",
        "prob_home_win",
    ]

    # keep only columns that actually exist (to avoid errors)
    cols_to_send = [c for c in cols_to_send if c in filtered.columns]

    records = filtered[cols_to_send].to_dict(orient="records")
    return jsonify(records)

@app.route("/api/upcoming_matches")
def get_upcoming_from_stats():
    league = request.args.get("league")
    season = request.args.get("season", type=int)
    limit = request.args.get("limit", default=100, type=int)

    sub = df_stats.copy()

    # Filter by league
    if league and "league" in sub.columns:
        sub = sub[sub["league"] == league]

    # Filter by season
    if season is not None and "season" in sub.columns:
        sub = sub[sub["season"] == season]  # same as your pandas check

    # Upcoming = unfinished = both goals empty
    if "home_goals" in sub.columns and "away_goals" in sub.columns:
        home_empty = sub["home_goals"].isna() | (sub["home_goals"] == "")
        away_empty = sub["away_goals"].isna() | (sub["away_goals"] == "")
        sub = sub[home_empty & away_empty]

    # Just for debug: print how many rows we got
    print(
        f"[upcoming_from_stats] league={league}, season={season}, rows={len(sub)}"
    )

    # Sort by date if present
    if "date" in sub.columns:
        sub = sub.sort_values("date", ascending=True)

    # Apply limit
    sub = sub.head(limit)

    cols_to_send = [
        "fixture_id",
        "league",
        "season",
        "date",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
        "prob_home_win",
        "prob_draw",
        "prob_away_win",
    ]
    cols_to_send = [c for c in cols_to_send if c in sub.columns]

    #  select only the needed columns
    sub = sub[cols_to_send].copy()

    # convert all NaN to None so JSON is valid
    sub = sub.replace({np.nan: None})

    records = sub.to_dict(orient="records")
    return jsonify(records)

@app.route("/api/seasons")
def get_seasons():

    # Return all seasons available, optionally filtered by league.

    league = request.args.get("league")

    sub = df.copy()
    if league:
        sub = sub[sub["league"] == league]

    if "season" not in sub.columns or sub.empty:
        return jsonify([])

    seasons = sorted(sub["season"].unique(), reverse=True)

    # ensure JSON-serializable ints
    seasons = [int(s) for s in seasons]

    print(f"[GET /api/seasons] league={league}, seasons={seasons}")
    return jsonify(seasons)


@app.route("/api/matches/<int:fixture_id>")
def get_match_detail(fixture_id: int):
    sub = df[df["fixture_id"] == fixture_id]
    if sub.empty:
        return jsonify({"error": "Match not found"}), 404
    return jsonify(sub.iloc[0].to_dict())

@app.route("/api/leagues")
def get_leagues():
    import pandas as pd

    df = pd.read_csv("data_api_football/All_matches_features.csv")

    leagues = (
        df[["league"]]
        .drop_duplicates()
        .sort_values("league")
        .reset_index(drop=True)
    )

    return leagues.to_dict(orient="records")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
