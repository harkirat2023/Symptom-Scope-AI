"""
ml.preprocessing.preprocess
============================
Utilities for encoding symptom inputs into binary feature vectors.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

from ml.constants import SYMPTOM_LIST

_SYMPTOM_INDEX: dict[str, int] = {s: i for i, s in enumerate(SYMPTOM_LIST)}


def encode_symptoms(symptoms: list[str]) -> np.ndarray:
    """Encode a list of symptom names into a binary numpy vector."""
    encoded = np.zeros(len(SYMPTOM_LIST), dtype=int)
    for symptom in symptoms:
        idx = _SYMPTOM_INDEX.get(symptom.lower().replace(" ", "_"))
        if idx is not None:
            encoded[idx] = 1
    return encoded


def symptoms_to_feature_row(symptoms: list[str]) -> list[int]:
    return encode_symptoms(symptoms).tolist()


def dataframe_from_records(
    records: list[tuple[list[int], str]],
) -> pd.DataFrame:
    df = pd.DataFrame([feat for feat, _ in records], columns=SYMPTOM_LIST)
    df["disease"] = [label for _, label in records]
    return df


def encode_labels(labels: list[str]) -> tuple[np.ndarray, LabelEncoder]:
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(labels)
    return encoded, encoder
