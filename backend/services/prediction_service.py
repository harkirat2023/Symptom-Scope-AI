import numpy as np
from dataclasses import dataclass
from services.disease_registry import DISEASE_REGISTRY
from services.model_registry import (
    get_decision_tree,
    get_random_forest,
    get_naive_bayes,
    get_label_encoder,
    get_symptom_columns,
    get_rf_feature_importances,
)

CONFIDENCE_LABELS: list[tuple[float, float, str, str]] = [
    (0, 40, "Low", "The system has low confidence in this prediction; please consult a healthcare professional for proper diagnosis."),
    (40, 70, "Moderate", "The system is moderately confident in this prediction; consider consulting a healthcare provider."),
    (70, 90, "High", "The system is highly confident in this prediction."),
    (90, 101, "Very High", "The system is very highly confident in this prediction."),
]


@dataclass
class PredictionResult:
    primary_prediction: str
    confidence: float
    alternatives: list[str]
    top_contributing_symptoms: list[dict[str, float]]
    predicted_class_idx: int = 0
    top_probability: float = 0.0


class PredictionService:
    def predict(self, encoded_features: np.ndarray) -> PredictionResult:
        features_2d = encoded_features.reshape(1, -1)
        dt = get_decision_tree()
        rf = get_random_forest()
        nb = get_naive_bayes()
        encoder = get_label_encoder()
        symptom_cols = get_symptom_columns()

        dt_probs = dt.predict_proba(features_2d)
        rf_probs = rf.predict_proba(features_2d)
        nb_probs = nb.predict_proba(features_2d)
        avg_probs = (dt_probs + rf_probs + nb_probs) / 3
        top_indices = np.argsort(avg_probs[0])[::-1][:3]
        diseases = encoder.inverse_transform(top_indices)
        probabilities = avg_probs[0][top_indices]
        confidence = round(float(probabilities[0] * 100), 2)

        predicted_class_idx = int(encoder.transform([diseases[0]])[0])

        present_indices = np.where(features_2d[0] == 1)[0]
        importances = get_rf_feature_importances()
        total_imp = importances[present_indices].sum() if len(present_indices) > 0 else 1.0
        contributions = [
            {
                "symptom": symptom_cols[i],
                "importance": round(float(importances[i]), 4),
                "relative_contribution_pct": round(
                    float(importances[i] / total_imp * 100), 2
                ) if total_imp > 0 else 0.0,
            }
            for i in present_indices
        ]
        top_symptoms = sorted(
            contributions, key=lambda x: abs(x["importance"]), reverse=True
        )[:5]

        return PredictionResult(
            primary_prediction=diseases[0],
            confidence=confidence,
            alternatives=diseases[1:].tolist(),
            top_contributing_symptoms=top_symptoms,
            predicted_class_idx=predicted_class_idx,
            top_probability=round(float(probabilities[0]), 4),
        )

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
