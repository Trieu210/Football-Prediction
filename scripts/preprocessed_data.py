import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
API_FILE = DATA_DIR / "ALL_LEAGUES_matches_2023_2025.csv"
KAGGLE_PL_FILE = DATA_DIR / "PL_matches_2018_2024.csv"
OUTPUT_FILE = DATA_DIR / "MASTER_matches.csv"

def compute_label(h, a):
    if h > a: return 2
    if h < a: return 0
    return 1

def load_api(f):
    df = pd.read_csv(f, parse_dates=["utcDate","season_startDate"], low_memory=False)
    df = df[df["status"] == "FINISHED"].dropna(subset=["fullTime_home","fullTime_away"])
    out = pd.DataFrame()
    out["league_code"] = df["competition_code"]
    out["date"] = df["utcDate"].dt.date
    out["season"] = df["season_startDate"].dt.year
    out["home_team"] = df["homeTeam_name"]
    out["away_team"] = df["awayTeam_name"]
    out["home_goals"] = df["fullTime_home"].astype(int)
    out["away_goals"] = df["fullTime_away"].astype(int)
    if "label" in df: out["label"] = df["label"].astype(int)
    else: out["label"] = [compute_label(h,a) for h,a in zip(out["home_goals"],out["away_goals"])]
    return out

def load_kaggle_pl(f):
    df = pd.read_csv(f, parse_dates=["utcDate","season_startDate"], low_memory=False)
    df = df[df["status"]=="FINISHED"].dropna(subset=["fullTime_home","fullTime_away"])
    out = pd.DataFrame()
    out["league_code"] = df["competition_code"].fillna("PL")
    out["date"] = df["utcDate"].dt.date
    out["season"] = df["season_startDate"].dt.year
    out["home_team"] = df["homeTeam_name"]
    out["away_team"] = df["awayTeam_name"]
    out["home_goals"] = df["fullTime_home"].astype(int)
    out["away_goals"] = df["fullTime_away"].astype(int)
    if "label" in df: out["label"] = df["label"].astype(int)
    else: out["label"] = [compute_label(h,a) for h,a in zip(out["home_goals"],out["away_goals"])]
    return out

def main():
    a = load_api(API_FILE)
    b = load_kaggle_pl(KAGGLE_PL_FILE)
    df = pd.concat([a,b], ignore_index=True)
    df = df.drop_duplicates(subset=["league_code","date","home_team","away_team"])
    df.sort_values(["league_code","season","date"]).to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()
