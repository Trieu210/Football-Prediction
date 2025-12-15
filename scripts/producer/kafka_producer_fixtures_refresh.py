import json
from confluent_kafka import Producer
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apiCallsToCSVFiles.fetch_stats_matches import HEADERS
from scripts.api_football_live_helper import get_fixtures_by_league_season

BROKER = "localhost:9092"
TOPIC = "fixtures_refresh"
LEAGUE_IDS = [39, 140, 78, 135, 61]  #Premier League, La Liga, Bundesliga, Serie A, Ligue 1
SEASON  = 2025

def main():
    producer = Producer({'bootstrap.servers': BROKER})

    total = 0
    for league_id in LEAGUE_IDS:
        print(f"\nFetching fixtures for league={league_id}, season={SEASON}")
        items = get_fixtures_by_league_season(HEADERS, league_id=league_id, season=SEASON)
        print(f"  Got {len(items)} fixtures from API")

        for it in items:
            fixture = it.get("fixture", {}) or {}
            league = it.get("league", {}) or {}
            teams  = it.get("teams", {}) or {}
            goals  = it.get("goals", {}) or {}
            status = (fixture.get("status", {}) or {}).get("short")

            event = {
                "predict_mode": "refresh",  # indicate this is a full refresh event
                "fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "status_short": status,

                "league": league.get("name"),
                "season": league.get("season"),

                "home_team": (teams.get("home", {}) or {}).get("name"),
                "away_team": (teams.get("away", {}) or {}).get("name"),
                "home_team_id": (teams.get("home", {}) or {}).get("id"),
                "away_team_id": (teams.get("away", {}) or {}).get("id"),

                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),
            }

            producer.produce(TOPIC, value=json.dumps(event).encode("utf-8"))
            total += 1

        producer.flush() #ensure all messages for this league are sent
        print(f"  Published {len(items)} fixtures to Kafka topic '{TOPIC}'")

    print(f"\nDONE. Total fixtures published: {total}")

if __name__ == "__main__":
    main()