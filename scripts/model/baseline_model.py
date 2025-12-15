import pandas as pd
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


DATA_DIR = Path("data_api_football")
FEATURES_CSV = DATA_DIR / "All_matches_features.csv"   
OUTPUT_CSV = DATA_DIR / "matches_with_probs.csv"
MODEL_PATH = DATA_DIR / "logreg_model.pkl"
SCALER_PATH = DATA_DIR / "scaler.pkl"


def main():
    print("Loading features:", FEATURES_CSV)
    df = pd.read_csv(FEATURES_CSV)

    # Features used for the model
    feature_cols = [
        "diff_goals",
        "diff_shots",
        "diff_shots_inbox",
        "diff_possession",
        "diff_pass_accuracy",
        "diff_corners",
        "diff_fouls",
    ]

    # X = feature matrix, y = label (0=away, 1=draw, 2=home)
    X = df[feature_cols].values
    y = df["label"].values

    # Also keep track of original indices (just in case)
    indices = df.index.values

    # Train/test split
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X,
        y,
        indices,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Multinomial logistic regression
    model = LogisticRegression(
        multi_class="multinomial",
        solver="lbfgs",
        max_iter=2000,
        class_weight="balanced",
    )

    print("Training Logistic Regression model...")
    model.fit(X_train_scaled, y_train)

    # Evaluation
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")

    print("\n=== Logistic Regression Results ===")
    print("Accuracy:", round(acc, 4))
    print("Macro F1:", round(f1, 4))
    print("\nPer-class metrics:\n")
    print(classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    #  Save model and scaler for real-time use 
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("\nSaved model to:", MODEL_PATH)
    print("Saved scaler to:", SCALER_PATH)

    #  Compute probabilities for ALL rows and save to CSV 
    X_all_scaled = scaler.transform(X)
    proba = model.predict_proba(X_all_scaled)
    class_order = model.classes_.tolist()  # should be [0, 1, 2]

    df["prob_away_win"] = proba[:, class_order.index(0)]
    df["prob_draw"] = proba[:, class_order.index(1)]
    df["prob_home_win"] = proba[:, class_order.index(2)]

    print("\nSaving matches with probabilities to:", OUTPUT_CSV)
    df.to_csv(OUTPUT_CSV, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
