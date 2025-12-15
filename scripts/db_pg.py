import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from dotenv import load_dotenv
import math

load_dotenv()

def clean(v):
    # Convert pandas/numpy NaN → None
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None

    # pandas.Timestamp → datetime
    if hasattr(v, "to_pydatetime"):
        return v.to_pydatetime()

    # numpy scalars → python scalars
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass

    return v


def get_db_connection():
    return psycopg2.connect(
        host = os.getenv("PGHOST", "localhost"),
        port = os.getenv("PGPORT", "5432"),
        dbname = os.getenv("PGDATABASE"),
        user = os.getenv("PGUSER"),
        password = os.getenv("PGPASSWORD")
    )
 # Insert multiple fixture rows
def insert_fixtures(rows):
    if not rows:
        return 0

    sql = """
    INSERT INTO fixtures
      (fixture_id, league, season, date,
       home_team, away_team, home_team_id, away_team_id,
       home_goals, away_goals, status)
    VALUES %s
    ON CONFLICT (fixture_id) DO UPDATE SET
      league = EXCLUDED.league,
      season = EXCLUDED.season,
      date = EXCLUDED.date,
      home_team = EXCLUDED.home_team,
      away_team = EXCLUDED.away_team,
      home_team_id = EXCLUDED.home_team_id,
      away_team_id = EXCLUDED.away_team_id,
      home_goals = EXCLUDED.home_goals,
      away_goals = EXCLUDED.away_goals,
      status = EXCLUDED.status,
      updated_at = NOW();
    """

    values = [
        (
            clean(r["fixture_id"]),
            clean(r["league"]),
            clean(r["season"]),
            clean(r.get("date")),
            clean(r.get("home_team")),
            clean(r.get("away_team")),
            clean(r.get("home_team_id")),
            clean(r.get("away_team_id")),
            clean(r.get("home_goals")),
            clean(r.get("away_goals")),
            clean(r.get("status")),
        )
        for r in rows
    ]

    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            execute_values(cur, sql, values)
        return len(rows)
    finally:
        conn.close()

# Insert match stats row 
def insert_match_stats(fixture_id, stats: dict) -> int:
    sql = """
    INSERT INTO match_stats (
      fixture_id,
      home_shots_total, home_shots_inbox, home_possession, home_pass_accuracy, home_corners, home_fouls,
      away_shots_total, away_shots_inbox, away_possession, away_pass_accuracy, away_corners, away_fouls
    )
    VALUES (
      %(fixture_id)s,
      %(home_shots_total)s, %(home_shots_inbox)s, %(home_possession)s, %(home_pass_accuracy)s, %(home_corners)s, %(home_fouls)s,
      %(away_shots_total)s, %(away_shots_inbox)s, %(away_possession)s, %(away_pass_accuracy)s, %(away_corners)s, %(away_fouls)s
    )
    ON CONFLICT (fixture_id) DO UPDATE SET
      home_shots_total = EXCLUDED.home_shots_total,
      home_shots_inbox = EXCLUDED.home_shots_inbox,
      home_possession = EXCLUDED.home_possession,
      home_pass_accuracy = EXCLUDED.home_pass_accuracy,
      home_corners = EXCLUDED.home_corners,
      home_fouls = EXCLUDED.home_fouls,
      away_shots_total = EXCLUDED.away_shots_total,
      away_shots_inbox = EXCLUDED.away_shots_inbox,
      away_possession = EXCLUDED.away_possession,
      away_pass_accuracy = EXCLUDED.away_pass_accuracy,
      away_corners = EXCLUDED.away_corners,
      away_fouls = EXCLUDED.away_fouls,
      updated_at = NOW();
    """

    payload = {"fixture_id": fixture_id}
    payload.update({k: stats.get(k) for k in [
        "home_shots_total","home_shots_inbox","home_possession","home_pass_accuracy","home_corners","home_fouls",
        "away_shots_total","away_shots_inbox","away_possession","away_pass_accuracy","away_corners","away_fouls",
    ]})

    conn = get_db_connection() 
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, payload)
        return 1
    finally:
        conn.close()

# Insert prediction row
# def insert_prediction(fixture_id: int, probs: dict, meta: dict) -> int:
#     sql = """
#     INSERT INTO predictions (
#       fixture_id, league, season, home_team, away_team,
#       prob_away_win, prob_draw, prob_home_win
#     )
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#     ON CONFLICT (fixture_id) DO UPDATE SET
#       league = EXCLUDED.league,
#       season = EXCLUDED.season,
#       home_team = EXCLUDED.home_team,
#       away_team = EXCLUDED.away_team,
#       prob_away_win = EXCLUDED.prob_away_win,
#       prob_draw = EXCLUDED.prob_draw,
#       prob_home_win = EXCLUDED.prob_home_win,
#       created_at = NOW();
#     """
#     conn = get_db_connection()
#     try:
#         with conn, conn.cursor() as cur:
#             cur.execute(sql, (
#                 fixture_id,
#                 meta.get("league"),
#                 meta.get("season"),
#                 meta.get("home_team"),
#                 meta.get("away_team"),
#                 probs.get("prob_away_win"),
#                 probs.get("prob_draw"),
#                 probs.get("prob_home_win"),
#             ))
#         return 1
#     finally:
#         conn.close()

# Prematch Predictions: h2h features
def insert_prematch_prediction(fixture_id: int, probs: dict, meta: dict) -> int:
    sql = """
    INSERT INTO predictions_prematch (
      fixture_id, league, season, home_team, away_team,
      prob_away_win, prob_draw, prob_home_win
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (fixture_id) DO UPDATE SET
      league = EXCLUDED.league,
      season = EXCLUDED.season,
      home_team = EXCLUDED.home_team,
      away_team = EXCLUDED.away_team,
      prob_away_win = EXCLUDED.prob_away_win,
      prob_draw = EXCLUDED.prob_draw,
      prob_home_win = EXCLUDED.prob_home_win,
      created_at = NOW();
    """
    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
                fixture_id,
                meta.get("league"),
                meta.get("season"),
                meta.get("home_team"),
                meta.get("away_team"),
                probs.get("prob_away_win"),
                probs.get("prob_draw"),
                probs.get("prob_home_win"),
            ))
        return 1
    finally:
        conn.close()

#Live Predictions: match stats features
def insert_live_prediction(fixture_id: int, probs: dict, meta: dict) -> int:
    sql = """
    INSERT INTO predictions_live (
      fixture_id, league, season, home_team, away_team,
      prob_away_win, prob_draw, prob_home_win
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (fixture_id) DO UPDATE SET
      league = EXCLUDED.league,
      season = EXCLUDED.season,
      home_team = EXCLUDED.home_team,
      away_team = EXCLUDED.away_team,
      prob_away_win = EXCLUDED.prob_away_win,
      prob_draw = EXCLUDED.prob_draw,
      prob_home_win = EXCLUDED.prob_home_win,
      created_at = NOW();
    """
    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, (
                fixture_id,
                meta.get("league"),
                meta.get("season"),
                meta.get("home_team"),
                meta.get("away_team"),
                probs.get("prob_away_win"),
                probs.get("prob_draw"),
                probs.get("prob_home_win"),
            ))
        return 1
    finally:
        conn.close()

#Fetch fixtures needing h2h update
def fetch_fixtures_h2h(limit: int = 2000, stale_hours: int = 12):
    sql = f"""
    SELECT
        f.fixture_id,
        f.league,
        f.season,
        f.date,
        f.home_team_id,
        f.away_team_id
    FROM fixtures f
    LEFT JOIN prematch_h2h h
      ON h.fixture_id = f.fixture_id
    WHERE f.status = 'NS'
      AND f.home_team_id IS NOT NULL
      AND f.away_team_id IS NOT NULL
      AND (
            h.updated_at IS NULL
            OR h.updated_at < NOW() - INTERVAL '{stale_hours} hours'
          )
    ORDER BY f.date ASC NULLS LAST
    LIMIT %s;
    """
    conn = get_db_connection()
    try:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            # Return list of dicts
            return [dict(r) for r in (cur.fetchall() or [])]
    finally:
        conn.close()

# Insert prematch h2h features
def insert_prematch_h2h(rows: list[dict]) -> int:
    if not rows:
        return 0

    sql = """
    INSERT INTO prematch_h2h (
      fixture_id,
      h2h_last,
      h2h_matches,
      h2h_home_wins,
      h2h_draws,
      h2h_away_wins,
      h2h_home_goals_for,
      h2h_home_goals_against,
      h2h_home_goal_diff,
      updated_at
    )
    VALUES %s
    ON CONFLICT (fixture_id) DO UPDATE SET
      h2h_last = EXCLUDED.h2h_last,
      h2h_matches = EXCLUDED.h2h_matches,
      h2h_home_wins = EXCLUDED.h2h_home_wins,
      h2h_draws = EXCLUDED.h2h_draws,
      h2h_away_wins = EXCLUDED.h2h_away_wins,
      h2h_home_goals_for = EXCLUDED.h2h_home_goals_for,
      h2h_home_goals_against = EXCLUDED.h2h_home_goals_against,
      h2h_home_goal_diff = EXCLUDED.h2h_home_goal_diff,
      updated_at = NOW();
    """

    values = []
    for r in rows:
        values.append((
            int(r["fixture_id"]),
            int(r.get("h2h_last", 0)),
            int(r.get("h2h_matches", 0)),
            int(r.get("h2h_home_wins", 0)),
            int(r.get("h2h_draws", 0)),
            int(r.get("h2h_away_wins", 0)),
            float(r.get("h2h_home_goals_for", 0.0)),
            float(r.get("h2h_home_goals_against", 0.0)),
            float(r.get("h2h_home_goal_diff", 0.0)),
            None,  # updated_at handled by NOW()
        ))

    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            execute_values(cur, sql, values, page_size=500)
        conn.commit()
        return len(values)
    finally:
        conn.close()

# Fetch distinct leagues from fixtures
def fetch_leagues_from_db():
    sql = """
    SELECT DISTINCT league
    FROM fixtures
    ORDER BY league ASC;
    """
    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [r[0] for r in rows]
    finally:
        conn.close()

# Fetch distinct seasons from fixtures
def fetch_seasons_from_db(league: str | None = None):
    if league:
        sql = """
        SELECT DISTINCT season
        FROM fixtures
        WHERE league = %s AND season IS NOT NULL
        ORDER BY season DESC;
        """
        params = (league,)
    else:
        sql = """
        SELECT DISTINCT season
        FROM fixtures
        WHERE season IS NOT NULL
        ORDER BY season DESC;
        """
        params = None

    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [r[0] for r in rows]
    finally:
        conn.close()

# Fetch Probabilities
def fetch_matches_with_probs(league: str, season: int, limit: int = 300, upcoming_only: bool = False):
    """
    Returns fixtures joined with:
      - predictions_prematch (prematch probs)
      - predictions_live (live probs)
      - prob_source: 'live' | 'prematch' | null
    """
    where_extra = ""
    if upcoming_only:
        where_extra = "AND (f.status = 'NS' OR (f.home_goals IS NULL AND f.away_goals IS NULL))"

    sql = f"""
    SELECT
      f.fixture_id,
      f.league,
      f.season,
      f.date,
      f.home_team,
      f.away_team,
      f.home_goals,
      f.away_goals,
      f.status,

      -- choose live if present, otherwise prematch
      COALESCE(pl.prob_home_win, pp.prob_home_win) AS prob_home_win,
      COALESCE(pl.prob_draw,     pp.prob_draw)     AS prob_draw,
      COALESCE(pl.prob_away_win, pp.prob_away_win) AS prob_away_win,

      CASE
        WHEN pl.fixture_id IS NOT NULL THEN 'live'
        WHEN pp.fixture_id IS NOT NULL THEN 'prematch'
        ELSE NULL
      END AS prob_source

    FROM fixtures f
    LEFT JOIN predictions_prematch pp ON pp.fixture_id = f.fixture_id
    LEFT JOIN predictions_live     pl ON pl.fixture_id = f.fixture_id

    WHERE f.league = %s
      AND f.season = %s
      {where_extra}

    ORDER BY f.date ASC NULLS LAST
    LIMIT %s;
    """

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (league, season, limit))
            return cur.fetchall()
    finally:
        conn.close()

#
def fetch_live_predictions(limit: int = 50):
    sql = """
    SELECT
      f.fixture_id,
      f.league,
      f.season,
      f.date,
      f.home_team,
      f.away_team,
      f.home_goals,
      f.away_goals,
      p.prob_home_win,
      p.prob_draw,
      p.prob_away_win,
      p.created_at
    FROM predictions_live p
    JOIN fixtures f ON f.fixture_id = p.fixture_id
    ORDER BY p.created_at DESC
    LIMIT %s;
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()
    finally:
        conn.close()