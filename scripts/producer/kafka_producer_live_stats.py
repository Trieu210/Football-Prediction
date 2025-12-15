import json
import time
from confluent_kafka import Producer
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from apiCallsToCSVFiles.fetch_stats_matches import fetch_fixture_stats, BASE_URL, HEADERS
from api_football_live_helper import get_live_fixtures


BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "match_stats_raw"

IN_PLAY = {"1H","HT","2H","ET","BT","P","SUSP","INT","LIVE"} #statuses indicating match is live/in-play

POLL_LIVE_FIXTURES_INTERVAL = 10  #seconds between polling live fixtures
SLEEP_BETWEEN_FIXTURE_STATS = 0.15  #seconds between fetching stats for different fixtures
PUBLISH_DEDUP = True  #whether to deduplicate published events to Kafka

LEAGUE_IDS = {
    "Premier League": 39,
    "La Liga": 140,
    "Bundesliga": 78,
    "Serie A": 135,
    "Ligue 1": 61,
}

def make_signature(e: dict) -> str:
    """Create a simple signature string for deduplication of events."""
    keys = [
        "elapsed","status_short",
        "home_goals", "away_goals",
        "home_shots_total", "away_shots_total",
        "home_shots_inbox", "away_shots_inbox",
        "home_possession", "away_possession",
        "home_pass_accuracy", "away_pass_accuracy",
        "home_corners", "away_corners",
        "home_fouls", "away_fouls"
    ]
    return "|".join(str(e.get(k)) for k in keys)

def main():
    p = Producer({'bootstrap.servers': BROKER})
    last_signature_by_fixture = {}

    while True:
        print("\nPolling live fixtures")
        live_items = get_live_fixtures(HEADERS)
        in_play = []
        for item in live_items:
            fixture  = item.get("fixture", {}) or {}
            status = (fixture.get("status", {}) or {})
            short = status.get("short")
            if short not in IN_PLAY:
                continue  #skip non-live matches
            league  = item.get("league", {}) or {}
            # league_id = league.get("id")
            # if LEAGUE_IDS and league_id not in LEAGUE_IDS:
            #     continue  #skip non-target leagues
            teams = item.get("teams", {}) or {}
            goals = item.get("goals", {}) or {}
            home = teams.get("home", {}) or {}
            away = teams.get("away", {}) or {}
            elapsed = (status.get("elapsed") or 0)
            in_play.append({
                "fixture_id": fixture.get("id"),
                # "league_id": league.get("id"),
                "league": league.get("name"),
                "season": league.get("season"),
                "date": fixture.get("date"),
                "home_team": home.get("name"),
                "away_team": away.get("name"),
                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),
                "status_short": fixture.get("status", {}).get("short"),
                "elapsed": elapsed
            })
        # No live matches
        if not in_play:
            print(" No live/in-play matches found.")
            time.sleep(POLL_LIVE_FIXTURES_INTERVAL)
            continue # skip to next 

        print(f" Found {len(in_play)} live/in-play matches.")

        for f in in_play:
            fixture_id = f["fixture_id"]
            print(f"  Fetching stats for fixture_id={fixture_id}...")
            stats = fetch_fixture_stats(fixture_id, f["home_team"], f["away_team"])

            if not stats:
                print("   [WARNING] No stats found.")
                continue

            event = {"mode": "live", "fixture_id": fixture_id, **f, **stats}
            signature = make_signature(event)

            if PUBLISH_DEDUP:
                last_sig = last_signature_by_fixture.get(fixture_id)
                if last_sig == signature:
                    print("   No changes in stats. Skipping publish.")
                    continue
                last_signature_by_fixture[fixture_id] = signature

            p.produce(TOPIC, value=json.dumps(event).encode("utf-8"))
            p.flush()
            print("   Published stats to Kafka.")

            time.sleep(SLEEP_BETWEEN_FIXTURE_STATS)


if __name__ == "__main__":
    main()



        