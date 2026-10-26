"""
Training script for the House Price Prediction model.

Reads data from data/housing_data.csv, trains a Scikit-Learn Linear Regression model,
evaluates performance using MAE, RMSE, and R2 score, and persists the trained artifact
and evaluation metrics to the models/ directory.
"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


FEATURE_NAMES = ["area_sqft", "bedrooms", "bathrooms", "floors", "age_years"]
TARGET_NAME = "price_inr"


def train_and_evaluate(data_path: Path, model_dir: Path):
    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{data_path}'. Please run 'python data/generate_dataset.py' first."
        )

    print(f"[1/5] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)

    # Validate required columns
    missing_cols = set(FEATURE_NAMES + [TARGET_NAME]) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    X = df[FEATURE_NAMES]
    y = df[TARGET_NAME]

    print(f"[2/5] Splitting data into 80% train and 20% test sets (Total samples: {len(df)})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"[3/5] Training Linear Regression model on {len(X_train)} samples...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    print("[4/5] Evaluating model on unseen test set...")
    y_pred = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    coefficients = {
        feat: float(coef) for feat, coef in zip(FEATURE_NAMES, model.coef_)
    }
    intercept = float(model.intercept_)

    print("\n" + "=" * 50)
    print("      MODEL EVALUATION RESULTS (Linear Regression)")
    print("=" * 50)
    print(f"R-squared (R2) Score  : {r2:.4f} ({r2 * 100:.2f}% variance explained)")
    print(f"Mean Absolute Error   : Rs. {mae:,.2f}")
    print(f"Root Mean Squared Err : Rs. {rmse:,.2f}")
    print(f"Intercept             : Rs. {intercept:,.2f}")
    print("-" * 50)
    print("Learned Coefficients:")
    for feat, coef in coefficients.items():
        print(f"  - {feat:12s} : Rs. {coef:+12,.2f}")
    print("=" * 50 + "\n")

    # Persist model artifact
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / "house_price_model.joblib"
    metrics_file = model_dir / "metrics.json"

    print(f"[5/5] Saving model artifact to: {model_file}")
    joblib.dump(model, model_file)

    metrics_payload = {
        "algorithm": "Linear Regression (Ordinary Least Squares)",
        "framework": "scikit-learn",
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features": FEATURE_NAMES,
        "target": TARGET_NAME,
        "metrics": {
            "r2_score": round(r2, 4),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
        },
        "coefficients": {k: round(v, 2) for k, v in coefficients.items()},
        "intercept": round(intercept, 2),
    }

    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)
    print(f"Evaluation metrics saved to: {metrics_file}")
    print("\nTraining completed successfully!")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    data_file = base_dir / "data" / "housing_data.csv"
    model_directory = base_dir / "models"
    train_and_evaluate(data_file, model_directory)
