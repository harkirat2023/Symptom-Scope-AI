import hashlib
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

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

DISEASE_SYMPTOM_PATTERNS: dict[str, list[str]] = {
    "Common Cold": ["runny_nose", "sneezing", "sore_throat", "dry_cough", "headache", "fatigue"],
    "Allergy": ["sneezing", "runny_nose", "rash", "headache", "fatigue"],
    "Mild Food Poisoning": ["nausea", "vomiting", "diarrhea", "abdominal_pain", "fatigue"],
    "Influenza": ["fever", "dry_cough", "fatigue", "headache", "body_ache", "sore_throat", "chills", "runny_nose"],
    "Bronchitis": ["dry_cough", "fatigue", "chest_pain", "fever", "shortness_of_breath", "body_ache"],
    "Gastroenteritis": ["nausea", "vomiting", "diarrhea", "abdominal_pain", "fever", "fatigue", "body_ache"],
    "Migraine": ["headache", "nausea", "vomiting", "blurred_vision", "dizziness", "fatigue",
                  "sensitivity_to_light", "sensitivity_to_sound"],
    "Pneumonia": ["fever", "dry_cough", "fatigue", "shortness_of_breath", "chest_pain", "chills", "sweating", "body_ache"],
    "Heart Attack": ["chest_pain", "shortness_of_breath", "nausea", "sweating", "dizziness", "fatigue",
                     "arm_pain", "jaw_pain"],
    "Stroke": ["confusion", "blurred_vision", "headache", "dizziness", "muscle_weakness", "fatigue",
               "facial_drooping", "speech_difficulty"],
    "Severe Respiratory Distress": ["shortness_of_breath", "chest_pain", "dry_cough", "confusion", "fatigue", "fever"],
    "Malaria": ["fever", "chills", "sweating", "headache", "body_ache", "fatigue", "nausea", "vomiting"],
    "Dengue": ["fever", "headache", "body_ache", "joint_pain", "rash", "nausea", "vomiting", "fatigue"],
    "COVID-19": ["fever", "dry_cough", "fatigue", "loss_of_taste", "loss_of_smell", "headache",
                 "sore_throat", "shortness_of_breath", "body_ache"],
    "Epilepsy": ["seizure", "confusion", "fatigue", "headache", "muscle_weakness", "dizziness"],
}

SYMPTOM_NOISE_RATES: dict[str, float] = {
    "fever": 0.10, "dry_cough": 0.10, "fatigue": 0.20, "headache": 0.15,
    "sore_throat": 0.10, "body_ache": 0.15, "chest_pain": 0.05, "shortness_of_breath": 0.08,
    "nausea": 0.12, "vomiting": 0.10, "diarrhea": 0.10, "loss_of_taste": 0.05,
    "loss_of_smell": 0.05, "runny_nose": 0.10, "sneezing": 0.10, "joint_pain": 0.10,
    "chills": 0.10, "sweating": 0.12, "dizziness": 0.15, "abdominal_pain": 0.10,
    "rash": 0.10, "muscle_weakness": 0.10, "blurred_vision": 0.10, "confusion": 0.08,
    "seizure": 0.05, "arm_pain": 0.05, "jaw_pain": 0.05, "facial_drooping": 0.05,
    "speech_difficulty": 0.05, "sensitivity_to_light": 0.08, "sensitivity_to_sound": 0.08,
}


def _disease_seed(disease: str) -> int:
    return int(hashlib.md5(disease.encode()).hexdigest()[:8], 16)


def generate_samples(
    disease: str, pattern: list[str], num_samples: int
) -> list[tuple[list[int], str]]:
    samples = []
    seed = _disease_seed(disease)
    rng = np.random.RandomState(seed)
    for _ in range(num_samples):
        features = [0] * len(SYMPTOM_LIST)
        for symptom in pattern:
            if symptom in SYMPTOM_LIST:
                idx = SYMPTOM_LIST.index(symptom)
                noise_rate = SYMPTOM_NOISE_RATES.get(symptom, 0.15)
                if rng.random() > noise_rate:
                    features[idx] = 1
        extra_symptoms = rng.choice(
            [s for s in SYMPTOM_LIST if s not in pattern],
            size=rng.randint(0, 2),
            replace=False,
        )
        for s in extra_symptoms:
            idx = SYMPTOM_LIST.index(s)
            if rng.random() > 0.7:
                features[idx] = 1
        samples.append((features, disease))
    return samples


def print_confusion_matrix(cm: np.ndarray, classes: list[str]) -> None:
    max_name_len = max(len(c) for c in classes)
    fmt = f"{{:<{max_name_len + 2}}}"
    header = " " * (max_name_len + 2) + "".join(
        f"{c:>{max_name_len}}" for c in classes
    )
    print(header)
    for i, row in enumerate(cm):
        row_label = f"{classes[i]:<{max_name_len}}"
        row_vals = " ".join(f"{v:>{max_name_len}}" for v in row)
        print(f"  {row_label} {row_vals}")


def main():
    rng = np.random.RandomState(42)
    all_samples: list[tuple[list[int], str]] = []

    BASE_SAMPLES_PER_DISEASE = {
        "Common Cold": 300,
        "Allergy": 250,
        "Mild Food Poisoning": 200,
        "Influenza": 250,
        "Bronchitis": 200,
        "Gastroenteritis": 200,
        "Migraine": 200,
        "Pneumonia": 200,
        "Heart Attack": 150,
        "Stroke": 150,
        "Severe Respiratory Distress": 150,
        "Malaria": 200,
        "Dengue": 200,
        "COVID-19": 250,
        "Epilepsy": 150,
    }

    for disease, pattern in DISEASE_SYMPTOM_PATTERNS.items():
        n = BASE_SAMPLES_PER_DISEASE.get(disease, 200)
        samples = generate_samples(disease, pattern, n)
        all_samples.extend(samples)

    df = pd.DataFrame(
        [features for features, _ in all_samples],
        columns=SYMPTOM_LIST,
    )
    df["disease"] = [label for _, label in all_samples]

    X = df[SYMPTOM_LIST].values
    y = df["disease"].values

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    disease_classes = list(label_encoder.classes_)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    dt = DecisionTreeClassifier(
        max_depth=10, min_samples_split=4, min_samples_leaf=2, random_state=42
    )
    rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
    )

    dt.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    dt_cv = cross_val_score(dt, X_train, y_train, cv=cv, scoring="accuracy")
    rf_cv = cross_val_score(rf, X_train, y_train, cv=cv, scoring="accuracy")

    for model_name, model, cv_scores in [
        ("Decision Tree", dt, dt_cv),
        ("Random Forest", rf, rf_cv),
    ]:
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        print(f"\n{'='*60}")
        print(f"  {model_name}")
        print(f"{'='*60}")
        print(f"  Cross-val accuracy (5-fold): {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        print(f"  Test accuracy:              {acc:.4f}")
        print(f"  Weighted precision:         {precision:.4f}")
        print(f"  Weighted recall:            {recall:.4f}")
        print(f"  Weighted F1-score:          {f1:.4f}")

        cm = confusion_matrix(y_test, y_pred)
        print(f"\n  Confusion Matrix ({len(disease_classes)} classes):")
        print_confusion_matrix(cm, disease_classes)

        print(f"\n  Per-class metrics:")
        report = classification_report(
            y_test, y_pred, target_names=disease_classes, zero_division=0, digits=4
        )
        print(report)

    rf_y_pred = rf.predict(X_test)
    rf_f1_per_class = f1_score(y_test, rf_y_pred, average=None, zero_division=0)
    weak_classes = [
        (disease_classes[i], rf_f1_per_class[i])
        for i in np.argsort(rf_f1_per_class)[:3]
    ]
    print(f"\n  Bottom-3 classes by F1 (Random Forest):")
    for disease, f1_val in weak_classes:
        print(f"    {disease}: F1={f1_val:.4f}")

    model_dir = Path(__file__).parent.parent / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    models_path = model_dir
    joblib.dump(dt, models_path / "decision_tree_v1.pkl")
    joblib.dump(rf, models_path / "random_forest_v1.pkl")
    joblib.dump(label_encoder, models_path / "label_encoder_v1.pkl")
    joblib.dump(SYMPTOM_LIST, models_path / "symptom_columns_v1.pkl")

    print(f"\n  Model files saved to: {models_path}")
    print(f"  Diseases ({len(disease_classes)}): {disease_classes}")
    print(f"  Symptoms ({len(SYMPTOM_LIST)}): {SYMPTOM_LIST}")


if __name__ == "__main__":
    main()
