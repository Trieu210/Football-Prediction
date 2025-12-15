import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import time 
from confluent_kafka import Producer
from db_pg import fetch_fixtures_h2h

BROKER = "localhost:9092" 
TOPIC = "prematch_h2h"

LIMIT = 5000  #max fixtures to fetch per run
STALE_HOURS = 12  #only fetch fixtures with h2h data older than this
POLL_INTERVAL = 60  #seconds between polling for new fixtures
SLEEP_BETWEEN_FIXTURES = 0.01  #seconds between publishing different fixtures


def main():
    p = Producer({"bootstrap.servers": BROKER})

    while True:
        rows = fetch_fixtures_h2h(limit=LIMIT, stale_hours=STALE_HOURS)
        print(f"\n[PREMATCH PRODUCER] fetched {len(rows)} fixtures H2H")

        if not rows:
            time.sleep(POLL_INTERVAL)
            continue

        sent = 0
        for r in rows:
            fixture_id = r.get("fixture_id")
            home_id = r.get("home_team_id")
            away_id = r.get("away_team_id")
            dt = r.get("date")

            event = {
                "predict_mode": "prematch",   # IMPORTANT: consumer expects predict_mode :contentReference[oaicite:2]{index=2}
                "fixture_id": int(fixture_id),
                "home_team_id": int(home_id),
                "away_team_id": int(away_id),
                "league": r.get("league"),
                "season": r.get("season"),
                "date": dt.isoformat() if dt else None,
            }

            p.produce(TOPIC, value=json.dumps(event).encode("utf-8"))
            sent += 1

            # small throttle
            if SLEEP_BETWEEN_FIXTURES:
                time.sleep(SLEEP_BETWEEN_FIXTURES)

        p.flush()
        print(f"[PREMATCH PRODUCER] published {sent} messages to topic={TOPIC}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()