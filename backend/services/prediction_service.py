import numpy as np
import joblib
from pathlib import Path
from dataclasses import dataclass
from threading import Lock
from services.disease_registry import DISEASE_REGISTRY

CONFIDENCE_LABELS: list[tuple[float, float, str, str]] = [
    (0, 40, "Low", "The system has low confidence in this prediction; please consult a healthcare professional for proper diagnosis."),
    (40, 70, "Moderate", "The system is moderately confident in this prediction; consider consulting a healthcare provider."),
    (70, 90, "High", "The system is highly confident in this prediction."),
    (90, 101, "Very High", "The system is very highly confident in this prediction."),
]

_models_path = Path(__file__).parent.parent / "ml" / "models"

_cache: dict = {}
_cache_lock = Lock()


def _get_model(name: str):
    with _cache_lock:
        if name not in _cache:
            _cache[name] = joblib.load(_models_path / name)
        return _cache[name]


@dataclass
class PredictionResult:
    primary_prediction: str
    confidence: float
    alternatives: list[str]
    top_contributing_symptoms: list[dict[str, float]]
    predicted_class_idx: int = 0
    top_probability: float = 0.0


class PredictionService:
    def __init__(self):
        self._decision_tree = None
        self._random_forest = None
        self._label_encoder = None
        self._symptom_columns = None
        self._feature_importances = None

    @property
    def decision_tree(self):
        if self._decision_tree is None:
            self._decision_tree = _get_model("decision_tree_v1.pkl")
        return self._decision_tree

    @property
    def random_forest(self):
        if self._random_forest is None:
            self._random_forest = _get_model("random_forest_v1.pkl")
        return self._random_forest

    @property
    def label_encoder(self):
        if self._label_encoder is None:
            self._label_encoder = _get_model("label_encoder_v1.pkl")
        return self._label_encoder

    @property
    def symptom_columns(self):
        if self._symptom_columns is None:
            self._symptom_columns = _get_model("symptom_columns_v1.pkl")
        return self._symptom_columns

    @property
    def feature_importances(self):
        if self._feature_importances is None:
            self._feature_importances = self.random_forest.feature_importances_
        return self._feature_importances

    def predict(self, encoded_features: np.ndarray) -> PredictionResult:
        features_2d = encoded_features.reshape(1, -1)
        dt_probs = self.decision_tree.predict_proba(features_2d)
        rf_probs = self.random_forest.predict_proba(features_2d)
        avg_probs = (dt_probs + rf_probs) / 2
        top_indices = np.argsort(avg_probs[0])[::-1][:3]
        diseases = self.label_encoder.inverse_transform(top_indices)
        probabilities = avg_probs[0][top_indices]
        confidence = round(float(probabilities[0] * 100), 2)

        predicted_class_idx = int(
            self.label_encoder.transform([diseases[0]])[0]
        )

        return PredictionResult(
            primary_prediction=diseases[0],
            confidence=confidence,
            alternatives=diseases[1:].tolist(),
            top_contributing_symptoms=self._get_contributing_symptoms(
                encoded_features, self.feature_importances, probabilities[0],
            ),
            predicted_class_idx=predicted_class_idx,
            top_probability=round(float(probabilities[0]), 4),
        )

    def _get_contributing_symptoms(
        self,
        encoded_features: np.ndarray,
        importances: np.ndarray,
        top_probability: float = 0.0,
    ) -> list[dict[str, float]]:
        present_indices = np.where(encoded_features == 1)[0]
        total_importance = importances[present_indices].sum() if len(present_indices) > 0 else 1.0
        contributions = [
            {
                "symptom": self.symptom_columns[i],
                "importance": round(float(importances[i]), 4),
                "relative_contribution_pct": round(
                    float(importances[i] / total_importance * 100), 2
                ) if total_importance > 0 else 0.0,
            }
            for i in present_indices
        ]
        return sorted(
            contributions, key=lambda x: abs(x["importance"]), reverse=True
        )[:5]

    @staticmethod
    def get_confidence_info(confidence: float) -> dict[str, str]:
        for lo, hi, label, description in CONFIDENCE_LABELS:
            if lo <= confidence < hi:
                return {
                    "label": label,
                    "description": description,
                }
        return {
            "label": "Unknown",
            "description": "Confidence level could not be determined.",
        }

    @staticmethod
    def generate_explanation_summary(
        disease: str,
        confidence: float,
        alternatives: list[str],
        top_symptoms: list[dict[str, float]],
    ) -> str:
        symptom_names = [s["symptom"].replace("_", " ") for s in top_symptoms[:3]]
        symptom_text = ", ".join(symptom_names)

        disease_info = DISEASE_REGISTRY.get(disease)
        disease_description = (
            disease_info.description if disease_info else f"{disease}"
        )

        parts = [
            f"Based on your reported symptoms ({symptom_text}), "
            f"the most likely diagnosis is {disease}.",
        ]

        if disease_info:
            parts.append(disease_description)

        _, _, conf_label, _ = next(
            (lo, hi, lb, desc)
            for lo, hi, lb, desc in CONFIDENCE_LABELS
            if lo <= confidence < hi
        )

        if conf_label in ("High", "Very High"):
            parts.append(
                f"The system is {conf_label.lower()} confident ({confidence}%) in this assessment."
            )
        else:
            parts.append(
                f"The system is {conf_label.lower()} confident ({confidence}%) in this assessment, "
                "so it is important to consult a healthcare professional."
            )

        if alternatives:
            alt_text = ", ".join(alternatives)
            parts.append(
                f"Alternative possibilities considered include {alt_text}."
            )

        if top_symptoms:
            strong_symptoms = [
                s["symptom"].replace("_", " ")
                for s in top_symptoms
                if s.get("relative_contribution_pct", 0) > 20
            ]
            if strong_symptoms:
                parts.append(
                    f"The strongest contributing symptoms were: {', '.join(strong_symptoms)}."
                )

        return " ".join(parts)
