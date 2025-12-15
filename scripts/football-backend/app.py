from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date

from db_pg import (
    fetch_matches_with_probs,
    fetch_live_predictions,
    fetch_seasons_from_db,
    fetch_leagues_from_db
)

app = Flask(__name__)

# enable cors
CORS(app, resources={r"/api/*": {"origins": "*"}})


def _json_safe(v):
    # psycopg2 returns datetime objects; jsonify can't serialize them
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


def _rows_json_safe(rows):
    out = []
    for r in rows:
        out.append({k: _json_safe(v) for k, v in dict(r).items()})
    return out


@app.route("/")
def health():
    return "Backend is running. Try /api/leagues"

@app.route("/api/leagues")
def get_leagues():
    rows = fetch_leagues_from_db()
    return jsonify([{"league": r} for r in rows])

@app.route("/api/seasons")
def get_seasons():
    league = request.args.get("league")
    seasons = fetch_seasons_from_db(league)
    return jsonify(seasons)

@app.route("/api/matches")
def get_matches():
    limit = int(request.args.get("limit", 300))
    league = request.args.get("league")
    season = request.args.get("season")
    status = request.args.get("status")  # "NS" or "FT" etc.

    if not league or not season:
        return jsonify({"error": "league and season are required"}), 400

    upcoming_only = (status == "NS")

    rows = fetch_matches_with_probs(
        league=league,
        season=int(season),
        limit=limit,
        upcoming_only=upcoming_only,
    )
    # If status is provided (FT/NS/etc) filter it 
    if status:
        rows = [r for r in rows if str(r.get("status")) == status]

    return jsonify(_rows_json_safe(rows))
@app.route("/api/live_predictions")
def api_live_predictions():
    limit = request.args.get("limit", default=50, type=int)
    rows = fetch_live_predictions(limit)
    return jsonify(_rows_json_safe(rows))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
