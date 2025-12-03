import joblib
import numpy as np
from pathlib import Path

DATA_DIR = Path("data_api_football")
MODEL_PATH = DATA_DIR / "logreg_model.pkl"
SCALER_PATH = DATA_DIR / "scaler.pkl"

FEATURE_COLS = [
    "diff_goals",
    "diff_shots",
    "diff_shots_inbox",
    "diff_possession",
    "diff_pass_accuracy",
    "diff_corners",
    "diff_fouls",
]

# Load model and scaler once (at import time)
print("Loading model from:", MODEL_PATH)
model = joblib.load(MODEL_PATH)

print("Loading scaler from:", SCALER_PATH)
scaler = joblib.load(SCALER_PATH)


def predict_match_probs(diff_features: dict):
    
    # Put values into correct order and shape (1, n_features)
    x = np.array([[diff_features[col] for col in FEATURE_COLS]])
    x_scaled = scaler.transform(x)

    proba = model.predict_proba(x_scaled)[0]  # shape (3,)
    class_order = model.classes_.tolist()     # [0, 1, 2]

    return {
        "away_win": float(proba[class_order.index(0)]),
        "draw": float(proba[class_order.index(1)]),
        "home_win": float(proba[class_order.index(2)]),
    }


if __name__ == "__main__":
    sample = {
        "diff_goals": 1,
        "diff_shots": 2,
        "diff_shots_inbox": 1,
        "diff_possession": 4.0,
        "diff_pass_accuracy": 2.5,
        "diff_corners": 1,
        "diff_fouls": -1,
    }
    probs = predict_match_probs(sample)
    print("Test sample probabilities:", probs)
