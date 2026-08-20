from threading import Lock

import numpy as np

from services.model_registry import (
    get_label_encoder,
    get_random_forest,
    get_symptom_columns,
)


class ExplainabilityService:
    def __init__(self):
        self._explainer = None
        self._lock = Lock()

    @property
    def random_forest(self):
        return get_random_forest()

    @property
    def symptom_columns(self):
        return get_symptom_columns()

    @property
    def label_encoder(self):
        return get_label_encoder()

    @property
    def explainer(self):
        if self._explainer is None:
            with self._lock:
                if self._explainer is None:
                    import shap
                    self._explainer = shap.TreeExplainer(self.random_forest)
        return self._explainer

    def compute_shap_values(
        self, encoded_features: np.ndarray, predicted_class_idx: int
    ) -> tuple[float, np.ndarray]:
        features_2d = encoded_features.reshape(1, -1)
        shap_values = self.explainer.shap_values(
            features_2d, check_additivity=False
        )
        expected = self.explainer.expected_value

        if isinstance(expected, np.ndarray) and expected.ndim > 0:
            base_value = float(expected[predicted_class_idx])
        else:
            base_value = float(expected)

        if isinstance(shap_values, list):
            class_shap = shap_values[predicted_class_idx][0]
        elif shap_values.ndim == 3:
            class_shap = shap_values[0, :, predicted_class_idx]
        elif shap_values.ndim == 2:
            class_shap = shap_values[0]
        else:
            class_shap = shap_values

        return base_value, np.asarray(class_shap)

    def build_contributing_symptoms(
        self,
        encoded_features: np.ndarray,
        predicted_class_idx: int,
        top_probability: float,
    ) -> dict:
        base_value, shap_array = self.compute_shap_values(
            encoded_features, predicted_class_idx
        )

        present_indices = np.where(encoded_features == 1)[0]
        total_abs_shap = (
            np.abs(shap_array[present_indices]).sum()
            if len(present_indices) > 0
            else 1.0
        )

        contributions = [
            {
                "symptom": self.symptom_columns[i],
                "importance": round(float(np.abs(shap_array[i])), 4),
                "shap_value": round(float(shap_array[i]), 6),
                "relative_contribution_pct": (
                    round(float(np.abs(shap_array[i]) / total_abs_shap * 100), 2)
                    if total_abs_shap > 0
                    else 0.0
                ),
            }
            for i in present_indices
        ]

        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return {
            "base_value": round(base_value, 4),
            "top_contributing_symptoms": contributions[:5],
        }
