import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent  
CSV_PATH = DATA_DIR / "data_api_football" / "All_matches_features.csv"

df = pd.read_csv(CSV_PATH)
# This file MUST contain these columns to do the check
required = ["label", "diff_goals"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

# For each label, check the average diff_goals sign:
# If diff_goals is (home - away), then:
#   home-win label should have positive mean diff_goals
#   away-win label should have negative mean diff_goals
means = df.groupby("label")["diff_goals"].mean().sort_index()

print("Mean diff_goals per label:")
print(means)

print("\nInterpretation guide:")
print("- label with highest mean diff_goals is likely HOME win")
print("- label with lowest mean diff_goals is likely AWAY win")
print("- middle label is usually DRAW (or check % near 0)")
