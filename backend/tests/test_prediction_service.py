from unittest.mock import patch, MagicMock
import numpy as np
from services.prediction_service import PredictionService


class TestPredictionService:
    def setup_method(self):
        self.service = PredictionService()

    def _mock_models(self):
        dt_mock = MagicMock()
        rf_mock = MagicMock()
        le_mock = MagicMock()
        cols_mock = ["fever", "cough", "headache", "fatigue"]

        dt_mock.predict_proba.return_value = np.array([[0.2, 0.5, 0.3]])
        rf_mock.predict_proba.return_value = np.array([[0.1, 0.6, 0.3]])
        rf_mock.feature_importances_ = np.array([0.4, 0.3, 0.2, 0.1])
        le_mock.inverse_transform.return_value = np.array(["Influenza", "Common Cold", "Migraine"])

        return dt_mock, rf_mock, le_mock, cols_mock

    @patch("services.prediction_service._get_model")
    def test_predict_returns_prediction_result(self, mock_get_model):
        dt, rf, le, cols = self._mock_models()

        def side_effect(name):
            mapping = {
                "decision_tree_v1.pkl": dt,
                "random_forest_v1.pkl": rf,
                "label_encoder_v1.pkl": le,
                "symptom_columns_v1.pkl": cols,
            }
            return mapping[name]

        mock_get_model.side_effect = side_effect

        encoded = np.array([1, 1, 0, 0])
        result = self.service.predict(encoded)

        assert result.primary_prediction == "Influenza"
        assert result.confidence > 0
        assert len(result.alternatives) == 2
        assert len(result.top_contributing_symptoms) > 0

    def test_get_confidence_info_low(self):
        info = self.service.get_confidence_info(30.0)
        assert info["label"] == "Low"

    def test_get_confidence_info_moderate(self):
        info = self.service.get_confidence_info(55.0)
        assert info["label"] == "Moderate"

    def test_get_confidence_info_high(self):
        info = self.service.get_confidence_info(75.0)
        assert info["label"] == "High"

    def test_get_confidence_info_very_high(self):
        info = self.service.get_confidence_info(95.0)
        assert info["label"] == "Very High"

    def test_generate_explanation_summary(self):
        summary = self.service.generate_explanation_summary(
            disease="Influenza",
            confidence=85.0,
            alternatives=["Common Cold"],
            top_symptoms=[
                {"symptom": "fever", "importance": 0.4},
                {"symptom": "dry_cough", "importance": 0.3},
            ],
        )
        assert "Influenza" in summary
        assert "high" in summary.lower()
        assert "85.0%" in summary

    def test_generate_explanation_low_confidence(self):
        summary = self.service.generate_explanation_summary(
            disease="Influenza",
            confidence=35.0,
            alternatives=["Common Cold"],
            top_symptoms=[{"symptom": "fever", "importance": 0.4}],
        )
        assert "consult" in summary.lower()
