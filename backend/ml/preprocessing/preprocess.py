import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

SYMPTOM_LIST = [
    "fever", "dry_cough", "fatigue", "headache", "sore_throat",
    "body_ache", "chest_pain", "shortness_of_breath", "nausea",
    "vomiting", "diarrhea", "loss_of_taste", "loss_of_smell",
    "runny_nose", "sneezing", "joint_pain", "chills", "sweating",
    "dizziness", "abdominal_pain", "rash", "muscle_weakness",
    "blurred_vision", "confusion", "seizure",
    "arm_pain", "jaw_pain", "facial_drooping", "speech_difficulty",
    "sensitivity_to_light", "sensitivity_to_sound",
]

_SYMPTOM_INDEX = {s: i for i, s in enumerate(SYMPTOM_LIST)}


def encode_symptoms(symptoms: list[str]) -> np.ndarray:
    encoded = np.zeros(len(SYMPTOM_LIST), dtype=int)
    for symptom in symptoms:
        idx = _SYMPTOM_INDEX.get(symptom.lower().replace(" ", "_"))
        if idx is not None:
            encoded[idx] = 1
    return encoded


def symptoms_to_feature_row(symptoms: list[str]) -> list[int]:
    return encode_symptoms(symptoms).tolist()


def load_dataset_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"symptoms", "disease"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}")
    return df


def dataframe_from_records(
    records: list[tuple[list[int], str]],
    symptom_columns: list[str],
) -> pd.DataFrame:
    df = pd.DataFrame([feat for feat, _ in records], columns=symptom_columns)
    df["disease"] = [label for _, label in records]
    return df


def encode_labels(labels: list[str]) -> tuple[np.ndarray, LabelEncoder]:
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(labels)
    return encoded, encoder
