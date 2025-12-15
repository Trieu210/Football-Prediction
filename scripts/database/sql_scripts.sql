CREATE TABLE  fixtures (
  fixture_id BIGINT PRIMARY KEY,
  league TEXT NOT NULL,
  season INT NOT NULL,
  date TIMESTAMPTZ,
  home_team TEXT,
  away_team TEXT,
  home_goals INT,
  away_goals INT,
  status TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE fixtures
  ADD COLUMN IF NOT EXISTS home_team_id INT,
  ADD COLUMN IF NOT EXISTS away_team_id INT;

CREATE TABLE  match_stats (
  fixture_id BIGINT PRIMARY KEY REFERENCES fixtures(fixture_id) ON DELETE CASCADE,

  home_shots_total INT,
  home_shots_inbox INT,
  home_possession REAL,
  home_pass_accuracy REAL,
  home_corners INT,
  home_fouls INT,

  away_shots_total INT,
  away_shots_inbox INT,
  away_possession REAL,
  away_pass_accuracy REAL,
  away_corners INT,
  away_fouls INT,

  updated_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE  predictions (
  fixture_id BIGINT PRIMARY KEY REFERENCES fixtures(fixture_id) ON DELETE CASCADE,
  prob_away_win REAL,
  prob_draw REAL,
  prob_home_win REAL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add metadata columns to predictions table
alter table predictions
add column if not exists league TEXT,
add column season INT,
add column home_team TEXT,
add column away_team TEXT;

-- New table for prematch head-to-head statistics
CREATE TABLE  prematch_h2h (
  fixture_id BIGINT PRIMARY KEY REFERENCES fixtures(fixture_id) ON DELETE CASCADE,

  h2h_last INT,
  h2h_matches INT,
  h2h_home_wins INT,
  h2h_draws INT,
  h2h_away_wins INT,

  h2h_home_goals_for REAL,
  h2h_home_goals_against REAL,
  h2h_home_goal_diff REAL,

  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- New table for prematch predictions
CREATE TABLE IF NOT EXISTS predictions_prematch (
  fixture_id BIGINT PRIMARY KEY REFERENCES fixtures(fixture_id) ON DELETE CASCADE,
  league TEXT,
  season INT,
  home_team TEXT,
  away_team TEXT,
  prob_away_win REAL,
  prob_draw REAL,
  prob_home_win REAL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- New table for live predictions
CREATE TABLE IF NOT EXISTS predictions_live (
  fixture_id BIGINT PRIMARY KEY REFERENCES fixtures(fixture_id) ON DELETE CASCADE,
  league TEXT,
  season INT,
  home_team TEXT,
  away_team TEXT,
  prob_away_win REAL,
  prob_draw REAL,
  prob_home_win REAL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Migrate existing data from predictions to predictions_prematch
INSERT INTO predictions_prematch (
  fixture_id, league, season, home_team, away_team,
  prob_away_win, prob_draw, prob_home_win, created_at
)
SELECT
  fixture_id, league, season, home_team, away_team,
  prob_away_win, prob_draw, prob_home_win, created_at
FROM predictions
ON CONFLICT (fixture_id) DO UPDATE SET
  league = EXCLUDED.league,
  season = EXCLUDED.season,
  home_team = EXCLUDED.home_team,
  away_team = EXCLUDED.away_team,
  prob_away_win = EXCLUDED.prob_away_win,
  prob_draw = EXCLUDED.prob_draw,
  prob_home_win = EXCLUDED.prob_home_win,
  created_at = EXCLUDED.created_at;

-- Drop the old predictions table
ALTER TABLE predictions RENAME TO predictions_legacy;
