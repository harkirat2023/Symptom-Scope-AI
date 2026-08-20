from unittest.mock import MagicMock, patch

import numpy as np

from services.prediction_service import PredictionService


class TestPredictionService:
    def setup_method(self):
        self.service = PredictionService()

    def _mock_models(self):
        dt_mock = MagicMock(spec=["predict_proba", "n_features_in_", "n_classes_"])
        rf_mock = MagicMock(spec=["predict_proba", "feature_importances_", "n_features_in_", "n_classes_"])
        le_mock = MagicMock()
        cols_mock = ["fever", "cough", "headache", "fatigue"]

        dt_mock.n_features_in_ = 4
        dt_mock.n_classes_ = 3
        rf_mock.n_features_in_ = 4
        rf_mock.n_classes_ = 3
        dt_mock.predict_proba.return_value = np.array([[0.2, 0.5, 0.3]])
        rf_mock.predict_proba.return_value = np.array([[0.1, 0.6, 0.3]])
        rf_mock.feature_importances_ = np.array([0.4, 0.3, 0.2, 0.1])
        le_mock.classes_ = np.array(["Influenza", "Common Cold", "Migraine"])
        le_mock.inverse_transform.return_value = np.array(["Influenza", "Common Cold", "Migraine"])
        le_mock.transform.return_value = np.array([0])

        return dt_mock, rf_mock, le_mock, cols_mock

    @patch("services.prediction_service.get_decision_tree")
    @patch("services.prediction_service.get_random_forest")
    @patch("services.prediction_service.get_naive_bayes")
    @patch("services.prediction_service.get_label_encoder")
    @patch("services.prediction_service.get_symptom_columns")
    @patch("services.prediction_service.get_rf_feature_importances")
    def test_predict_returns_prediction_result(
        self, mock_importances, mock_cols, mock_le, mock_nb, mock_rf, mock_dt
    ):
        dt, rf, le, cols = self._mock_models()
        nb_mock = MagicMock()
        nb_mock.n_features_in_ = 4
        nb_mock.n_classes_ = 3
        nb_mock.predict_proba.return_value = np.array([[0.3, 0.4, 0.3]])

        mock_dt.return_value = dt
        mock_rf.return_value = rf
        mock_nb.return_value = nb_mock
        mock_le.return_value = le
        mock_cols.return_value = cols
        mock_importances.return_value = np.array([0.4, 0.3, 0.2, 0.1])

        encoded = np.array([[1, 1, 1, 0]])
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
