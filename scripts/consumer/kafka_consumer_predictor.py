
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.real_time_predictor_model import predict_match_probs

from confluent_kafka import Producer, Consumer
import json
from db_pg import insert_fixtures,insert_match_stats,insert_live_prediction


BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_LIVE = "match_stats_raw"
TOPIC_REFRESH = "fixtures_refresh"
TOPIC_OUTPUT = "match_predictions"

consumer = Consumer({
    "bootstrap.servers": BROKER,
    "group.id": "kafka_consumer_predictor_group",
    "auto.offset.reset": "earliest",
})

consumer.subscribe([TOPIC_LIVE, TOPIC_REFRESH])
producer = Producer({'bootstrap.servers': BROKER})

def to_diff(e: dict) -> dict:
    def n(x): return 0 if x is None else x

    elapsed = n(e.get("elapsed"))
    denom = max(15, min(elapsed, 120)) # cap at 120 mins, floor at 15 mins to avoid extreme values
    scale = 90.0 / denom
    # 
    def per90(x): return n(x) * scale

    return {
        "diff_goals": n(e.get("home_goals")) - n(e.get("away_goals")),
        # per-90 only for count stats
        "diff_shots": per90(e.get("home_shots_total")) - per90(e.get("away_shots_total")),
        "diff_shots_inbox": per90(e.get("home_shots_inbox")) - per90(e.get("away_shots_inbox")),
        "diff_corners": per90(e.get("home_corners")) - per90(e.get("away_corners")),
        "diff_fouls": per90(e.get("home_fouls")) - per90(e.get("away_fouls")),
        # percentage stats as-is
        "diff_possession": n(e.get("home_possession")) - n(e.get("away_possession")),
        "diff_pass_accuracy": n(e.get("home_pass_accuracy")) - n(e.get("away_pass_accuracy")),
    }

def normalize_prob_keys(p: dict) -> dict:
    if "prob_away_win" in p:
        return p
    return {
        "prob_home_win": p.get("home_win"),
        "prob_draw": p.get("draw"),
        "prob_away_win": p.get("away_win"),
    }

print("Kafka predictor consumer started. Waiting for messages...")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Kafka error:", msg.error())
        continue

    e = json.loads(msg.value().decode("utf-8"))
    mode = e.get("predict_mode") or e.get("mode") or "live"  #default to "live" mode

    fixture_id = int(e.get("fixture_id")) if e.get("fixture_id") is not None else None
    if fixture_id is None:
        print("Skipping message without fixture_id:", e)
        continue

    #REFRESH MODE
    if mode == "refresh":
        fixture_row = {
            "fixture_id": fixture_id,
            "league": e.get("league"),
            "season": int(e.get("season")) if e.get("season") is not None else None,
            "date": e.get("date"),
            "home_team": e.get("home_team"),
            "away_team": e.get("away_team"),
            "home_team_id": e.get("home_team_id"),
            "away_team_id": e.get("away_team_id"),
            "home_goals": e.get("home_goals"),
            "away_goals": e.get("away_goals"),
            "status": e.get("status_short"),
        }
        insert_fixtures([fixture_row])
        print(f"REFRESH UPSERT OK fixture={fixture_id} status={fixture_row['status']}")
        continue

    #LIVE MODE (exhisting fixture stats update + prediction)
    print(f"\nRECEIVED fixture_id={fixture_id}")

    try:
        fixture_row = {
            "fixture_id": fixture_id,
            "league": e.get("league"),
            "season": int(e.get("season")) if e.get("season") is not None else None,
            "date": e.get("date"),
            "home_team": e.get("home_team"),
            "away_team": e.get("away_team"),
            "home_goals": e.get("home_goals"),
            "away_goals": e.get("away_goals"),
            "status": e.get("status_short"),
        }
        insert_fixtures([fixture_row])

        stats = {
            "home_shots_total": e.get("home_shots_total"),
            "home_shots_inbox": e.get("home_shots_inbox"),
            "home_possession": e.get("home_possession"),
            "home_pass_accuracy": e.get("home_pass_accuracy"),
            "home_corners": e.get("home_corners"),
            "home_fouls": e.get("home_fouls"),
            "away_shots_total": e.get("away_shots_total"),
            "away_shots_inbox": e.get("away_shots_inbox"),
            "away_possession": e.get("away_possession"),
            "away_pass_accuracy": e.get("away_pass_accuracy"),
            "away_corners": e.get("away_corners"),
            "away_fouls": e.get("away_fouls"),
        }
        insert_match_stats(fixture_id, stats)

        diff = to_diff(e)
        probs = normalize_prob_keys(predict_match_probs(diff))

        meta = {
            "league": e.get("league"),
            "season": int(e.get("season")) if e.get("season") is not None else None,
            "home_team": e.get("home_team"),
            "away_team": e.get("away_team"),
        }
        insert_live_prediction(fixture_id, probs, meta)

        producer.produce(TOPIC_OUTPUT, value=json.dumps({"fixture_id": fixture_id, **probs}).encode("utf-8"))
        producer.flush()

        print(f"DB WRITE OK for fixture {fixture_id}")

    except Exception as ex:
        print("CONSUMER FAILED:", repr(ex))
        raise



            # test = diff.copy()
        # test["diff_goals"] = -2
        # print("TEST(-2 goals) =>", normalize_prob_keys(predict_match_probs(test)))

        # test["diff_goals"] = +2
        # print("TEST(+2 goals) =>", normalize_prob_keys(predict_match_probs(test)))
        # print("home_goals:", e.get("home_goals"), "away_goals:", e.get("away_goals"))   