from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

DATA_DIR = Path("data_api_football")
INPUT_CSV = DATA_DIR / "All_matches_2018-2025_with_stats.csv"
OUTPUT_CSV = DATA_DIR / "All_matches_2018-2025_with_stats_and_match_probs.csv"


def main():
    print("Loading data from:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)

    required = ["league", "season", "home_team", "away_team", "home_goals", "away_goals"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    #  Split finished vs upcoming 
    finished_mask = df["home_goals"].notna() & df["away_goals"].notna()
    finished = df[finished_mask].copy()
    upcoming = df[~finished_mask].copy()

    print("Total rows:       ", len(df))
    print("Finished matches: ", len(finished))
    print("Upcoming matches: ", len(upcoming))

    #  Build target label for finished matches: H / D / A 
    finished["target"] = np.where(
        finished["home_goals"] > finished["away_goals"],
        "H",
        np.where(finished["home_goals"] < finished["away_goals"], "A", "D"),
    )

    print("\nResult distribution (H/D/A):")
    print(finished["target"].value_counts(normalize=True))

    #  Select pre-match features 
    # These are the ONLY things you know before kick-off with your current CSV.
    feature_cols = ["league", "season", "home_team", "away_team"]

    # One-hot encode on the FULL dataset so train/upcoming share the same columns
    X_full = pd.get_dummies(df[feature_cols], drop_first=False)
    X_train = X_full.loc[finished.index]
    y_train = finished["target"]

    # Train multinomial Logistic Regression 
    print("\nTraining LogisticRegression on finished matches...")
    model = LogisticRegression(
        max_iter=2000,
        multi_class="multinomial",
        solver="lbfgs",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # training accuracy check
    train_acc = model.score(X_train, y_train)
    print(f"Training accuracy: {train_acc:.3f}")

    #  Predict probabilities for ALL matches (finished + upcoming)
    proba_all = model.predict_proba(X_full)
    classes = model.classes_.tolist()  # e.g. ['A', 'D', 'H']

    def col_idx(label: str) -> int:
        return classes.index(label) if label in classes else None

    idx_H = col_idx("H")
    idx_D = col_idx("D")
    idx_A = col_idx("A")

    # Initialize columns
    df["prob_home_win"] = np.nan
    df["prob_draw"] = np.nan
    df["prob_away_win"] = np.nan

    if idx_H is not None:
        df["prob_home_win"] = proba_all[:, idx_H]
    if idx_D is not None:
        df["prob_draw"] = proba_all[:, idx_D]
    if idx_A is not None:
        df["prob_away_win"] = proba_all[:, idx_A]

    # Save to new CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print("\nSaved match-level probabilities to:", OUTPUT_CSV)
    print("Rows:", len(df))


if __name__ == "__main__":
    main()
