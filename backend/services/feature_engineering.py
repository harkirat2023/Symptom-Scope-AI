"""
services.feature_engineering
==============================
Encodes incoming symptom names into binary feature vectors for model inference.
SYMPTOM_LIST is imported from ml.constants — single source of truth.
"""

import numpy as np

from ml.constants import SYMPTOM_LIST

_SYMPTOM_INDEX: dict[str, int] = {s: i for i, s in enumerate(SYMPTOM_LIST)}


class FeatureEngineeringService:
    def encode_symptoms(self, symptoms: list[str]) -> np.ndarray:
        encoded = np.zeros(len(SYMPTOM_LIST), dtype=int)
        for symptom in symptoms:
            index = _SYMPTOM_INDEX.get(symptom.lower().replace(" ", "_"))
            if index is not None:
                encoded[index] = 1
        return encoded
