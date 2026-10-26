"""
House Price Prediction Flask Web Application.

Provides RESTful endpoints and dashboard UI for real-time house price estimation
using Scikit-Learn Linear Regression. Prediction history is maintained in-memory
for the active server session without persistent database overhead.
"""

import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from model import HousePricePredictor, format_inr, format_inr_compact

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-house-price-prediction-secret-key")
app.config["JSON_SORT_KEYS"] = False

# Thread-safe in-memory session history store
# Note: Memory state is maintained per server worker process and resets when the service restarts.
# No persistent database is used, adhering to lightweight demonstration design.
session_lock = threading.Lock()
session_history: List[Dict[str, Any]] = []

# Initialize model predictor singleton at startup
try:
    predictor = HousePricePredictor()
    model_loaded = True
    load_error_message = None
except Exception as exc:
    predictor = None
    model_loaded = False
    load_error_message = str(exc)
    print(f"[ERROR] Failed to initialize HousePricePredictor on startup: {exc}")


def get_session_stats() -> Dict[str, Any]:
    """Calculate aggregate statistics across the current active session."""
    with session_lock:
        total = len(session_history)
        if total == 0:
            return {
                "total_predictions": 0,
                "latest_price": "—",
                "latest_price_compact": "—",
                "average_price": "—",
                "average_price_compact": "—",
                "history": [],
            }

        prices = [item["raw_price"] for item in session_history]
        latest_val = prices[-1]
        avg_val = sum(prices) / total

        return {
            "total_predictions": total,
            "latest_price": format_inr(latest_val),
            "latest_price_compact": format_inr_compact(latest_val),
            "average_price": format_inr(avg_val),
            "average_price_compact": format_inr_compact(avg_val),
            "history": list(session_history),  # Return snapshot
        }


@app.route("/", methods=["GET"])
def index():
    """Render main dashboard view."""
    stats = get_session_stats()
    model_info = predictor.get_model_info() if predictor else {}
    return render_template(
        "index.html",
        stats=stats,
        model_info=model_info,
        model_loaded=model_loaded,
        load_error_message=load_error_message,
    )


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handle house price prediction requests.
    Accepts both application/json and application/x-www-form-urlencoded payloads.
    """
    if not model_loaded or predictor is None:
        return (
            jsonify({
                "success": False,
                "error": "Machine learning model is not loaded. Please ensure train_model.py has been executed.",
            }),
            503,
        )

    # Extract payload regardless of Content-Type
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    # Backend validation
    is_valid, parsed_data, error_msg = predictor.validate_inputs(data)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    try:
        prediction_result = predictor.predict(parsed_data)

        # Store in session memory (thread-safe)
        record = {
            "id": len(session_history) + 1,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "features": parsed_data,
            "raw_price": prediction_result["raw_price"],
            "formatted_price": prediction_result["formatted_price"],
            "compact_price": prediction_result["compact_price"],
        }

        with session_lock:
            session_history.append(record)

        stats = get_session_stats()

        return jsonify({
            "success": True,
            "data": {
                "prediction": prediction_result,
                "stats": stats,
            },
        })

    except Exception as exc:
        return (
            jsonify({
                "success": False,
                "error": f"An unexpected error occurred during prediction: {str(exc)}",
            }),
            500,
        )


@app.route("/history", methods=["GET"])
def get_history():
    """Return JSON history of session predictions for dynamic frontend charting."""
    stats = get_session_stats()
    return jsonify({"success": True, "data": stats})


@app.route("/health", methods=["GET"])
def health():
    """Deployment monitoring and AWS ALB health check endpoint."""
    status_code = 200 if model_loaded else 503
    return (
        jsonify({
            "status": "healthy" if model_loaded else "unhealthy",
            "model_loaded": model_loaded,
            "service": "House Price Prediction Service",
            "algorithm": "Linear Regression",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_session_predictions": len(session_history),
        }),
        status_code,
    )


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api") or request.is_json:
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    return render_template("index.html", stats=get_session_stats(), model_info={}, model_loaded=model_loaded), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"Starting House Price Prediction Flask app on http://{host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
