import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import time
from confluent_kafka import Consumer

from db_pg import insert_prematch_h2h
from api_football_live_helper import get_head_to_head

BROKER = "localhost:9092"
TOPIC = "prematch_h2h"
API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-apisports-key": API_KEY
}
LAST_H2H = 10  #number of last h2h matches to fetch
SLEEP_BETWEEN_API_CALLS = 0.05  #seconds between API calls to avoid rate limits

def build_h2h_features(fixtures: list[dict], fixture_id: int, home_team_id: int, away_team_id: int) -> dict:
    home_wins = 0
    away_wins = 0
    draws = 0
    gf_sum = 0
    ga_sum = 0
    matches_counted = 0

    for item in fixtures:
        teams = item.get("teams", {}) or {}
        goals = item.get("goals", {}) or {}

        home = teams.get("home", {}) or {}
        away = teams.get("away", {}) or {}

        match_home_id = home.get("id")
        match_away_id = away.get("id")
        home_goals = goals.get("home")
        away_goals = goals.get("away")

        if match_home_id is None or match_away_id is None:
            continue
        if home_goals is None or away_goals is None:
            continue

        match_home_id = int(match_home_id)
        match_away_id = int(match_away_id)
        home_goals = int(home_goals)
        away_goals = int(away_goals)

        if match_home_id == home_team_id and match_away_id == away_team_id:
            goals_for = home_goals
            goals_against = away_goals
        elif match_home_id == away_team_id and match_away_id == home_team_id:
            goals_for = away_goals
            goals_against = home_goals
        else:
            continue

        matches_counted += 1
        gf_sum += goals_for
        ga_sum += goals_against

        if goals_for > goals_against:
            home_wins += 1
        elif goals_for < goals_against:
            away_wins += 1
        else:
            draws += 1

    # defaults
    goals_for_avg = gf_sum / matches_counted if matches_counted else 0.0
    goals_against_avg = ga_sum / matches_counted if matches_counted else 0.0
    goals_diff_avg = (gf_sum - ga_sum) / matches_counted if matches_counted else 0.0

    return {
        "fixture_id": int(fixture_id),
        "h2h_last": int(LAST_H2H),
        "h2h_matches": int(matches_counted),
        "h2h_home_wins": int(home_wins),
        "h2h_draws": int(draws),
        "h2h_away_wins": int(away_wins),
        "h2h_home_goals_for": float(goals_for_avg),
        "h2h_home_goals_against": float(goals_against_avg),
        "h2h_home_goal_diff": float(goals_diff_avg),
    }

 
def main():
    consumer = Consumer({
        'bootstrap.servers': BROKER,
        'group.id': 'prematch_h2h_consumer_group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([TOPIC])
    print(f"[PREMATCH H2H CONSUMER] listening topic={TOPIC} broker={BROKER}")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Kafka error:", msg.error())
            continue
        
        e = json.loads(msg.value().decode("utf-8"))
        fixture_id = e.get("fixture_id")
        home_team_id = e.get("home_team_id")
        away_team_id = e.get("away_team_id")
        league = e.get("league")
        season = e.get("season")

        if fixture_id is None or home_team_id is None or away_team_id is None:
            print("Skipping message with missing ids", e)
            continue
        
        fixture_id = int(fixture_id)
        home_team_id = int(home_team_id)
        away_team_id = int(away_team_id)

        try:
            fixtures = get_head_to_head(
                HEADERS,
                home_team_id,
                away_team_id,
                last=LAST_H2H,
                timeout=25
            )
            print(f"[DEBUG] fixture_id={fixture_id} api_returned={len(fixtures)} league={league} season={season}")
            row = build_h2h_features(fixtures, fixture_id, home_team_id, away_team_id)
            inserted = insert_prematch_h2h([row])

            print(
                f"fixture_id={fixture_id} "
                f"used={row['h2h_matches']} W/D/L={row['h2h_home_wins']}/{row['h2h_draws']}/{row['h2h_away_wins']} "
                f"GF={row['h2h_home_goals_for']:.2f} GA={row['h2h_home_goals_against']:.2f} GD={row['h2h_home_goal_diff']:.2f}"
            )

            if SLEEP_BETWEEN_API_CALLS:
                time.sleep(SLEEP_BETWEEN_API_CALLS)

        except Exception as ex:
            print(f"[FAILED] fixture_id={fixture_id} err={repr(ex)}")


if __name__ == "__main__":
    main()





   


