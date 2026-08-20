import numpy as np

from services.feature_engineering import SYMPTOM_LIST, FeatureEngineeringService


class TestFeatureEngineeringService:
    def setup_method(self):
        self.service = FeatureEngineeringService()

    def test_encode_empty_symptoms(self):
        result = self.service.encode_symptoms([])
        assert isinstance(result, np.ndarray)
        assert result.shape == (len(SYMPTOM_LIST),)
        assert np.all(result == 0)

    def test_encode_known_symptom(self):
        result = self.service.encode_symptoms(["fever"])
        assert result[SYMPTOM_LIST.index("fever")] == 1
        assert np.sum(result) == 1

    def test_encode_multiple_symptoms(self):
        result = self.service.encode_symptoms(["fever", "dry_cough", "headache"])
        assert result[SYMPTOM_LIST.index("fever")] == 1
        assert result[SYMPTOM_LIST.index("dry_cough")] == 1
        assert result[SYMPTOM_LIST.index("headache")] == 1
        assert np.sum(result) == 3

    def test_encode_unknown_symptom_ignored(self):
        result = self.service.encode_symptoms(["unknown_symptom"])
        assert np.all(result == 0)

    def test_encode_case_insensitive(self):
        result_upper = self.service.encode_symptoms(["FEVER"])
        result_mixed = self.service.encode_symptoms(["Dry Cough"])
        assert result_upper[SYMPTOM_LIST.index("fever")] == 1
        assert result_mixed[SYMPTOM_LIST.index("dry_cough")] == 1

    def test_encode_duplicate_symptoms(self):
        result = self.service.encode_symptoms(["fever", "fever", "fever"])
        assert result[SYMPTOM_LIST.index("fever")] == 1
        assert np.sum(result) == 1
