
-- 1) Fixtures (match info)
CREATE TABLE IF NOT EXISTS fixtures (
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

-- 2) Match statistics 
CREATE TABLE IF NOT EXISTS match_stats (
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


-- 3) Predictions
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

