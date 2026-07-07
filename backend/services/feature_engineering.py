import numpy as np

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


class FeatureEngineeringService:
    def encode_symptoms(self, symptoms: list[str]) -> np.ndarray:
        encoded = np.zeros(len(SYMPTOM_LIST), dtype=int)
        for symptom in symptoms:
            index = _SYMPTOM_INDEX.get(symptom.lower().replace(" ", "_"))
            if index is not None:
                encoded[index] = 1
        return encoded
