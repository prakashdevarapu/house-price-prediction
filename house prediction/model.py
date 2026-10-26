"""
Model service module for House Price Prediction.

Handles model loading, feature validation, prediction execution,
and Indian Rupee formatting. Keeps prediction logic strictly separated
from Flask web route handlers.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib
import pandas as pd


# Exact feature ordering expected by the trained Scikit-Learn model
FEATURE_NAMES = ["area_sqft", "bedrooms", "bathrooms", "floors", "age_years"]

# Reasonable physical bounds for validation
FEATURE_LIMITS = {
    "area_sqft": {"min": 100.0, "max": 25000.0, "label": "Area (sq ft)"},
    "bedrooms": {"min": 1, "max": 20, "label": "Bedrooms"},
    "bathrooms": {"min": 1, "max": 15, "label": "Bathrooms"},
    "floors": {"min": 1, "max": 10, "label": "Floors"},
    "age_years": {"min": 0.0, "max": 150.0, "label": "Age of Property (years)"},
}


def format_inr(number: float) -> str:
    """
    Format a numeric amount into Indian Currency notation (₹ xx,xx,xxx).
    For example:
        1250000 -> ₹12,50,000
        10500000 -> ₹1,05,00,000
    """
    rounded = int(round(number))
    if rounded < 0:
        return f"-₹{format_inr(abs(rounded))[1:]}"

    s = str(rounded)
    if len(s) <= 3:
        return f"₹{s}"

    # Last 3 digits
    last_three = s[-3:]
    remaining = s[:-3]

    # Group the remaining digits in pairs of 2 from right to left
    pairs = []
    while len(remaining) > 2:
        pairs.append(remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        pairs.append(remaining)

    pairs.reverse()
    formatted = ",".join(pairs) + "," + last_three
    return f"₹{formatted}"


def format_inr_compact(amount: float) -> str:
    """
    Return human-readable Indian unit string (e.g. ₹45.20 Lakhs or ₹1.35 Cr).
    """
    amt = float(amount)
    if amt >= 10000000:  # 1 Crore = 10,000,000
        return f"₹{amt / 10000000:.2f} Cr"
    elif amt >= 100000:  # 1 Lakh = 100,000
        return f"₹{amt / 100000:.2f} Lakh"
    else:
        return format_inr(amt)


class HousePricePredictor:
    """
    Encapsulates the trained Linear Regression model, its metadata,
    and prediction methods.
    """

    def __init__(self, model_path: Optional[Path] = None, metrics_path: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parent
        self.model_path = model_path or (base_dir / "models" / "house_price_model.joblib")
        self.metrics_path = metrics_path or (base_dir / "models" / "metrics.json")
        self.model = None
        self.metrics: Dict[str, Any] = {}
        self.load_model()

    def load_model(self) -> None:
        """Load trained model and metrics from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at '{self.model_path}'. "
                f"Please run 'python train_model.py' first."
            )

        self.model = joblib.load(self.model_path)

        if self.metrics_path.exists():
            try:
                with open(self.metrics_path, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)
            except Exception as e:
                print(f"[Warning] Could not load metrics file: {e}")
                self.metrics = {}

    def validate_inputs(self, raw_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, float]], Optional[str]]:
        """
        Validate raw input dictionary against type and range rules.
        Returns:
            (is_valid, parsed_data_dict_or_none, error_message_or_none)
        """
        parsed: Dict[str, float] = {}

        for feature in FEATURE_NAMES:
            raw_val = raw_data.get(feature)

            # Check existence and non-empty
            if raw_val is None or str(raw_val).strip() == "":
                label = FEATURE_LIMITS[feature]["label"]
                return False, None, f"Missing required field: {label}."

            # Check numeric conversion
            try:
                val = float(raw_val)
            except (ValueError, TypeError):
                label = FEATURE_LIMITS[feature]["label"]
                return False, None, f"Invalid value for {label}. Please enter a valid number."

            # Check bounds
            limits = FEATURE_LIMITS[feature]
            if val < limits["min"]:
                return (
                    False,
                    None,
                    f"{limits['label']} cannot be less than {limits['min']}.",
                )
            if val > limits["max"]:
                return (
                    False,
                    None,
                    f"{limits['label']} exceeds reasonable upper limit of {limits['max']}.",
                )

            # Ensure bedrooms, bathrooms, floors are integers or integer-like
            if feature in ["bedrooms", "bathrooms", "floors"]:
                if not float(val).is_integer():
                    return False, None, f"{limits['label']} must be a whole integer."
                parsed[feature] = int(val)
            else:
                parsed[feature] = val

        return True, parsed, None

    def predict(self, input_features: Dict[str, float]) -> Dict[str, Any]:
        """
        Run inference with strictly preserved feature ordering.
        Returns detailed prediction dictionary.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded. Call load_model() first.")

        # Construct DataFrame with exact column order
        df = pd.DataFrame([input_features], columns=FEATURE_NAMES)
        raw_price = float(self.model.predict(df)[0])

        # Floor prediction at a minimum realistic salvage value (e.g. ₹5 Lakhs)
        bounded_price = max(raw_price, 500000.0)

        return {
            "raw_price": round(bounded_price, 2),
            "formatted_price": format_inr(bounded_price),
            "compact_price": format_inr_compact(bounded_price),
            "features": input_features,
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata and metrics."""
        return {
            "algorithm": self.metrics.get("algorithm", "Linear Regression"),
            "framework": self.metrics.get("framework", "scikit-learn"),
            "trained_at": self.metrics.get("trained_at", "N/A"),
            "metrics": self.metrics.get("metrics", {"r2_score": 0.0, "mae": 0.0, "rmse": 0.0}),
            "coefficients": self.metrics.get("coefficients", {}),
            "intercept": self.metrics.get("intercept", 0.0),
            "total_samples": self.metrics.get("total_samples", 0),
        }
