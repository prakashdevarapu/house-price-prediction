"""
Unit and Integration Tests for House Price Prediction System.

Covers:
1. Model loading and persistence integrity
2. Input validation (positive, negative, boundaries, zero area, missing fields)
3. Inference mathematical sanity and Indian Rupee formatting
4. Web endpoints: GET /, POST /predict (JSON and form), GET /health, GET /history
"""

import json
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from model import HousePricePredictor, format_inr, format_inr_compact


@pytest.fixture
def client():
    """Create Flask test client fixture."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def predictor():
    """Create predictor instance fixture."""
    return HousePricePredictor()


# ============================================================================
# 1. Model & Valuation Service Unit Tests
# ============================================================================

def test_model_loaded(predictor):
    """Verify that the model loads successfully with valid coefficients."""
    assert predictor.model is not None
    info = predictor.get_model_info()
    assert info["algorithm"].startswith("Linear Regression")
    assert "metrics" in info
    assert info["metrics"]["r2_score"] > 0.80


def test_format_inr():
    """Verify Indian currency notation formatting."""
    assert format_inr(4500000) == "₹45,00,000"
    assert format_inr(12500000) == "₹1,25,00,000"
    assert format_inr(85000) == "₹85,000"
    assert format_inr(500) == "₹500"


def test_format_inr_compact():
    """Verify compact human-readable Lakhs and Crores formatting."""
    assert "Lakh" in format_inr_compact(4500000)
    assert "Cr" in format_inr_compact(12500000)


def test_valid_input_validation(predictor):
    """Verify valid inputs parse cleanly."""
    valid_payload = {
        "area_sqft": 1500,
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 1,
        "age_years": 5,
    }
    is_valid, parsed, error = predictor.validate_inputs(valid_payload)
    assert is_valid is True
    assert error is None
    assert parsed["area_sqft"] == 1500.0
    assert parsed["bedrooms"] == 3


def test_missing_feature_validation(predictor):
    """Verify validation rejects missing fields."""
    incomplete_payload = {
        "area_sqft": 1500,
        "bedrooms": 3,
        # missing bathrooms, floors, age_years
    }
    is_valid, parsed, error = predictor.validate_inputs(incomplete_payload)
    assert is_valid is False
    assert parsed is None
    assert "Missing required field" in error


def test_zero_or_negative_area_validation(predictor):
    """Verify validation rejects zero or negative area."""
    zero_area = {
        "area_sqft": 0,
        "bedrooms": 2,
        "bathrooms": 1,
        "floors": 1,
        "age_years": 1,
    }
    is_valid, _, error = predictor.validate_inputs(zero_area)
    assert is_valid is False
    assert "cannot be less than 100" in error

    negative_area = dict(zero_area, area_sqft=-500)
    is_valid, _, error = predictor.validate_inputs(negative_area)
    assert is_valid is False


def test_non_numeric_validation(predictor):
    """Verify validation rejects strings or non-numeric values."""
    bad_data = {
        "area_sqft": "huge",
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 1,
        "age_years": 0,
    }
    is_valid, _, error = predictor.validate_inputs(bad_data)
    assert is_valid is False
    assert "valid number" in error


def test_prediction_output_structure(predictor):
    """Verify prediction returns expected keys and realistic positive price."""
    features = {
        "area_sqft": 1800.0,
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 2,
        "age_years": 3.0,
    }
    res = predictor.predict(features)
    assert "raw_price" in res
    assert "formatted_price" in res
    assert "compact_price" in res
    assert res["raw_price"] > 1000000  # Should be > ₹10 Lakhs


# ============================================================================
# 2. Flask Route Integration Tests
# ============================================================================

def test_index_route(client):
    """Verify GET / renders 200 OK and contains key dashboard markers."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "House Price Prediction" in html
    assert "Linear Regression" in html
    assert "Built-up Area" in html


def test_health_route(client):
    """Verify GET /health returns 200 and healthy JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["algorithm"] == "Linear Regression"


def test_predict_endpoint_json_valid(client):
    """Verify POST /predict with valid JSON payload returns 200 and formatted price."""
    payload = {
        "area_sqft": 1600,
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 1,
        "age_years": 4,
    }
    response = client.post(
        "/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "prediction" in data["data"]
    assert "stats" in data["data"]
    assert data["data"]["stats"]["total_predictions"] >= 1


def test_predict_endpoint_form_valid(client):
    """Verify POST /predict with valid form data returns 200."""
    form_data = {
        "area_sqft": "2200",
        "bedrooms": "4",
        "bathrooms": "3",
        "floors": "2",
        "age_years": "2",
    }
    response = client.post("/predict", data=form_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["prediction"]["raw_price"] > 0


def test_predict_endpoint_invalid_input(client):
    """Verify POST /predict with invalid data returns 400 Bad Request."""
    bad_payload = {
        "area_sqft": -100,  # Negative area
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 1,
        "age_years": 4,
    }
    response = client.post(
        "/predict",
        data=json.dumps(bad_payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "error" in data


def test_history_endpoint(client):
    """Verify GET /history returns current session snapshot."""
    response = client.get("/history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "total_predictions" in data["data"]
