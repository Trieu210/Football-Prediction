from ..db_pg import get_db_connection, insert_prematch_prediction
DEFAULT = {"prob_home_win": 1/3, "prob_draw": 1/3, "prob_away_win": 1/3}

def h2h_probs(n, hw, d, aw):
    # Laplace smoothing
    if n is None or n <= 0:
        return DEFAULT

    hw = hw or 0
    d = d or 0
    aw = aw or 0

    denom = n + 3
    return {
        "prob_home_win": (hw + 1) / denom,
        "prob_draw": (d + 1) / denom,
        "prob_away_win": (aw + 1) / denom,
    }

def main(limit=5000):
    sql = """
    SELECT
      f.fixture_id, f.league, f.season, f.home_team, f.away_team,
      h.h2h_matches, h.h2h_home_wins, h.h2h_draws, h.h2h_away_wins
    FROM fixtures f
    JOIN prematch_h2h h ON h.fixture_id = f.fixture_id
    WHERE f.status = 'NS'
    ORDER BY f.date ASC NULLS LAST
    LIMIT %s;
    """

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
    finally:
        conn.close()

    for r in rows:
        row = dict(zip(cols, r))
        fixture_id = int(row["fixture_id"])

        probs = h2h_probs(
            row.get("h2h_matches"),
            row.get("h2h_home_wins"),
            row.get("h2h_draws"),
            row.get("h2h_away_wins"),
        )

        meta = {
            "league": row.get("league"),
            "season": row.get("season"),
            "home_team": row.get("home_team"),
            "away_team": row.get("away_team"),
        }

        insert_prematch_prediction(fixture_id, probs, meta)

    print(f"[DONE] wrote {len(rows)} H2H-only prematch predictions")

if __name__ == "__main__":
    main()