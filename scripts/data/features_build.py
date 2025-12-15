import pandas as pd
from pathlib import Path

DATA_DIR = Path("data_api_football")
INPUT_CSV = DATA_DIR / "All_matches_2018-2025_with_stats.csv"
OUTPUT_CSV = DATA_DIR / "All_matches_features.csv"

ROLLING_WINDOW = 10
MIN_MATCHES = 5  # minimum previous matches for rolling to be valid


def main():
    print("Loading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    # Basic cleaning / typing
    df["season"] = df["season"].astype(int)
    df["date"] = pd.to_datetime(df["date"])

    # Stats from home side perspective
    home_cols = {
        "home_team": "team",
        "away_team": "opponent",
        "home_goals": "goals_for",
        "away_goals": "goals_against",
        "home_shots_total": "shots_total",
        "home_shots_inbox": "shots_inbox",
        "home_possession": "possession",
        "home_pass_accuracy": "pass_accuracy",
        "home_corners": "corners",
        "home_fouls": "fouls",
    }

    home_df = df[
        ["league", "season", "date", "fixture_id"] + list(home_cols.keys())
    ].rename(columns=home_cols)
    home_df["is_home"] = 1

    # Stats from away side perspective
    away_cols = {
        "away_team": "team",
        "home_team": "opponent",
        "away_goals": "goals_for",
        "home_goals": "goals_against",
        "away_shots_total": "shots_total",
        "away_shots_inbox": "shots_inbox",
        "away_possession": "possession",
        "away_pass_accuracy": "pass_accuracy",
        "away_corners": "corners",
        "away_fouls": "fouls",
    }

    away_df = df[
        ["league", "season", "date", "fixture_id"] + list(away_cols.keys())
    ].rename(columns=away_cols)
    away_df["is_home"] = 0

    team_df = pd.concat([home_df, away_df], ignore_index=True)

    # Compute rolling averages over previous 10 games per team
    stat_cols = [
        "goals_for",
        "shots_total",
        "shots_inbox",
        "possession",
        "pass_accuracy",
        "corners",
        "fouls",
    ]

    team_df = team_df.sort_values(["league", "season", "team", "date"])

    # groupby + rolling + shift(1) to use ONLY previous matches
    rolling_avgs = (
        team_df.groupby(["league", "season", "team"])[stat_cols]
        .apply(
            lambda g: g.rolling(window=ROLLING_WINDOW, min_periods=MIN_MATCHES)
            .mean()
            .shift(1)
        )
        .reset_index(level=[0, 1, 2], drop=True)
    )

    for col in stat_cols:
        team_df[f"avg_{col}"] = rolling_avgs[col]

    # Pull home/away rolling avgs back to match level 
    # Home team rolling stats per fixture
    home_avgs = (
        team_df[team_df["is_home"] == 1][["fixture_id"] + [f"avg_{c}" for c in stat_cols]]
        .rename(
            columns={
                f"avg_{c}": f"home_avg_{c}"
                for c in stat_cols
            }
        )
    )

    # Away team rolling stats per fixture
    away_avgs = (
        team_df[team_df["is_home"] == 0][["fixture_id"] + [f"avg_{c}" for c in stat_cols]]
        .rename(
            columns={
                f"avg_{c}": f"away_avg_{c}"
                for c in stat_cols
            }
        )
    )

    features = df.merge(home_avgs, on="fixture_id", how="left").merge(
        away_avgs, on="fixture_id", how="left"
    )

    # Create difference features (home - away)
    features["diff_goals"] = features["home_avg_goals_for"] - features["away_avg_goals_for"]
    features["diff_shots"] = features["home_avg_shots_total"] - features["away_avg_shots_total"]
    features["diff_shots_inbox"] = (
        features["home_avg_shots_inbox"] - features["away_avg_shots_inbox"]
    )
    features["diff_possession"] = (
        features["home_avg_possession"] - features["away_avg_possession"]
    )
    features["diff_pass_accuracy"] = (
        features["home_avg_pass_accuracy"] - features["away_avg_pass_accuracy"]
    )
    features["diff_corners"] = features["home_avg_corners"] - features["away_avg_corners"]
    features["diff_fouls"] = features["home_avg_fouls"] - features["away_avg_fouls"]

    # Create label: 2 = home win, 1 = draw, 0 = away win 
    def label_result(row):
        h = row["home_goals"]
        a = row["away_goals"]
        if pd.isna(h) or pd.isna(a):
            return None
        if h > a:
            return 2
        elif h == a:
            return 1
        else:
            return 0

    features["label"] = features.apply(label_result, axis=1)

    #  Drop rows with insufficient history / missing label 
    diff_cols = [
        "diff_goals",
        "diff_shots",
        "diff_shots_inbox",
        "diff_possession",
        "diff_pass_accuracy",
        "diff_corners",
        "diff_fouls",
    ]

    before = len(features)
    features = features.dropna(subset=diff_cols + ["label"])
    after = len(features)
    print(f"Dropped {before - after} rows due to insufficient history / missing label.")

    #  Keep only what needed for training
    keep_cols = [
        "league",
        "season",
        "date",
        "fixture_id",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
        "label",
    ] + diff_cols

    features = features[keep_cols].sort_values(["season", "league", "date"])

    print("Final training rows:", len(features))
    print("Saving to:", OUTPUT_CSV)
    features.to_csv(OUTPUT_CSV, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
