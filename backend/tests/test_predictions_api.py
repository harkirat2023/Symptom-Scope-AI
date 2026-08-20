from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_predict_symptoms(client, mock_db):
    with patch("services.prediction_service.PredictionService.predict") as mock_predict, \
         patch("services.prediction_service.PredictionService.get_confidence_info") as mock_conf_info, \
         patch("services.prediction_service.PredictionService.generate_explanation_summary") as mock_explain, \
         patch("services.feature_engineering.FeatureEngineeringService.encode_symptoms") as mock_encode, \
         patch("services.explainability_service.ExplainabilityService.build_contributing_symptoms") as mock_shap:

        mock_encode.return_value = np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        mock_predict.return_value = MagicMock(
            primary_prediction="Influenza",
            confidence=85.5,
            alternatives=["Common Cold"],
            top_contributing_symptoms=[
                {"symptom": "fever", "importance": 0.4},
                {"symptom": "dry_cough", "importance": 0.3},
            ],
        )
        mock_conf_info.return_value = {
            "label": "High",
            "description": "High confidence",
        }
        mock_explain.return_value = "Explanation summary"
        mock_shap.return_value = {
            "base_value": 0.1234,
            "top_contributing_symptoms": [
                {"symptom": "fever", "importance": 0.4, "shap_value": 0.1, "relative_contribution_pct": 57.14},
                {"symptom": "dry_cough", "importance": 0.3, "shap_value": 0.05, "relative_contribution_pct": 28.57},
            ],
        }

        mock_db.insert_one.return_value = MagicMock(
            inserted_id="507f1f77bcf86cd799439011"
        )

        response = client.post(
            "/api/v1/predict",
            json={
                "symptoms": ["fever", "cough"],
                "age": 30,
                "gender": "male",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["primary_prediction"] == "Influenza"
        assert data["confidence"] == 85.5
        assert "Common Cold" in data["alternatives"]
        assert data["severity"] is not None
        assert data["prediction_id"] is not None


def test_predict_symptoms_shows_validation_error(client):
    response = client.post(
        "/api/v1/predict",
        json={},
    )
    assert response.status_code == 422


def test_predict_empty_symptoms_error(client):
    response = client.post(
        "/api/v1/predict",
        json={"symptoms": []},
    )
    assert response.status_code == 422


def test_predict_invalid_pain_level(client):
    response = client.post(
        "/api/v1/predict",
        json={
            "symptoms": ["fever"],
            "pain_level": 15,
        },
    )
    assert response.status_code == 422


def test_doctors_endpoint(client):
    response = client.get("/api/v1/doctors")
    assert response.status_code == 200
    data = response.json()
    assert "doctors" in data
    assert "total" in data
    assert "specialties" in data
    assert "locations" in data
    assert data["total"] > 0


def test_doctors_filter_by_specialty(client):
    response = client.get("/api/v1/doctors?specialty=Cardiologist")
    assert response.status_code == 200
    data = response.json()
    assert all("Cardiologist" in d["specialty"] for d in data["doctors"])


def test_symptoms_search(client):
    response = client.get("/api/v1/symptoms/search?q=fever")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0


def test_symptoms_search_by_category(client):
    response = client.get("/api/v1/symptoms/search?category=Respiratory")
    assert response.status_code == 200
    data = response.json()
    assert all(r["category"] == "Respiratory" for r in data["results"])


def test_hospitals_endpoint(client):
    response = client.get("/api/v1/hospitals")
    assert response.status_code == 200
    data = response.json()
    assert "hospitals" in data
    assert "total" in data


def test_hospitals_filter_emergency(client):
    response = client.get("/api/v1/hospitals?emergency_only=true")
    assert response.status_code == 200
    data = response.json()
    assert all(h["emergency"] for h in data["hospitals"])


def test_analytics_endpoint(client, mock_db):
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_db.find.return_value = mock_cursor

    response = client.get("/api/v1/analytics/test-user-id?range=6m")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data


def test_reports_endpoint(client, mock_db):
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_db.find.return_value = mock_cursor

    response = client.get("/api/v1/reports/test-user-id")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
