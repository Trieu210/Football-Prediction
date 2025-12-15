from confluent_kafka import Producer
import json

BROKER = "localhost:9092"
TOPIC = "match_stats_raw"

p = Producer({'bootstrap.servers': BROKER})

event = {
    "fixture_id": 999999,
    "league": "Premier League",
    "season": 2025,
    "date": "2025-12-13T20:00:00Z",
    "home_team": "Test Home",
    "away_team": "Test Away",
    "home_goals": 1,
    "away_goals": 0,

    "home_shots_total": 10,
    "home_shots_inbox": 5,
    "home_possession": 55.0,
    "home_pass_accuracy": 82.0,
    "home_corners": 4,
    "home_fouls": 7,

    "away_shots_total": 7,
    "away_shots_inbox": 2,
    "away_possession": 45.0,
    "away_pass_accuracy": 78.0,
    "away_corners": 3,
    "away_fouls": 10
}

p.produce(TOPIC, value=json.dumps(event).encode("utf-8"))
p.flush()
print("Sent one test event to Kafka.")