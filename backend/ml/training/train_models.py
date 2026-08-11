"""
ml.training.train_models
=========================
SymptomScope AI — Model Training Pipeline

Trains Decision Tree, Random Forest, and Naive Bayes classifiers for
disease prediction. Uses the Symptom2Disease Kaggle dataset as the primary
data source, augmented with a small synthetic set for emergency/rare diseases
not covered by the Kaggle dataset.

Usage:
    # Train on Kaggle + augmented synthetic data (recommended):
    python -m ml.training.train_models

    # Force synthetic-only (offline fallback):
    python -m ml.training.train_models --synthetic-only
"""

import argparse
import hashlib
import logging

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier


logger = logging.getLogger("symptomscope.training")

from ml.constants import SYMPTOM_LIST
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "ml" / "models"

# ---------------------------------------------------------------------------
# Synthetic augmentation for diseases not covered in the Kaggle dataset.
# Keeps the training pipeline working offline and adds emergency diseases.
# ---------------------------------------------------------------------------

_AUGMENT_PATTERNS: dict[str, list[str]] = {
    "Heart Attack": [
        "chest_pain", "shortness_of_breath", "nausea", "sweating",
        "dizziness", "fatigue", "arm_pain", "jaw_pain",
    ],
    "Stroke": [
        "confusion", "blurred_vision", "headache", "dizziness",
        "muscle_weakness", "fatigue", "facial_drooping", "speech_difficulty",
    ],
    "Severe Respiratory Distress": [
        "shortness_of_breath", "chest_pain", "cough", "confusion",
        "fatigue", "fever",
    ],
    "COVID-19": [
        "fever", "dry_cough", "fatigue", "loss_of_taste", "loss_of_smell",
        "headache", "sore_throat", "shortness_of_breath", "body_ache",
    ],
    "Epilepsy": [
        "seizure", "confusion", "fatigue", "headache",
        "muscle_weakness", "dizziness",
    ],
}

_AUGMENT_SAMPLES = 80  # samples per augmented disease
_NOISE_RATE = 0.12     # probability of flipping a signal symptom off


def _disease_seed(disease: str) -> int:
    return int(hashlib.md5(disease.encode()).hexdigest()[:8], 16)


def _generate_augmented(disease: str, pattern: list[str], n: int) -> pd.DataFrame:
    """Generate synthetic binary rows for a single disease."""
    rng = np.random.RandomState(_disease_seed(disease))
    symptom_idx = {s: i for i, s in enumerate(SYMPTOM_LIST)}
    rows = []
    for _ in range(n):
        vec = np.zeros(len(SYMPTOM_LIST), dtype=int)
        for sym in pattern:
            idx = symptom_idx.get(sym)
            if idx is not None and rng.random() > _NOISE_RATE:
                vec[idx] = 1
        rows.append(vec)
    df = pd.DataFrame(rows, columns=SYMPTOM_LIST)
    df["disease"] = disease
    return df


def build_augmented_df() -> pd.DataFrame:
    """Return a DataFrame with synthetic rows for emergency diseases."""
    frames = [
        _generate_augmented(d, p, _AUGMENT_SAMPLES)
        for d, p in _AUGMENT_PATTERNS.items()
    ]
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Synthetic-only fallback (used when Kaggle download is unavailable)
# ---------------------------------------------------------------------------

_SYNTHETIC_PATTERNS: dict[str, list[str]] = {
    "Common Cold": ["runny_nose", "sneezing", "sore_throat", "cough", "headache", "fatigue"],
    "Allergy": ["sneezing", "runny_nose", "rash", "headache", "fatigue", "watering_from_eyes"],
    "Influenza": ["fever", "cough", "fatigue", "headache", "body_ache", "sore_throat", "chills"],
    "Bronchial Asthma": ["cough", "fatigue", "chest_pain", "breathlessness", "phlegm"],
    "Pneumonia": ["fever", "cough", "fatigue", "shortness_of_breath", "chest_pain", "chills", "sweating"],
    "Migraine": ["headache", "nausea", "vomiting", "blurred_vision", "dizziness", "sensitivity_to_light"],
    "Dengue": ["fever", "headache", "body_ache", "joint_pain", "rash", "nausea", "fatigue"],
    "Malaria": ["fever", "chills", "sweating", "headache", "body_ache", "fatigue", "nausea"],
    "Typhoid": ["high_fever", "headache", "nausea", "vomiting", "stomach_pain", "fatigue", "toxic_look_typhos"],
    "Jaundice": ["itching", "vomiting", "fatigue", "weight_loss", "high_fever", "dark_urine", "yellowing_of_eyes", "abdominal_pain"],
    "Chicken Pox": ["itching", "skin_rash", "fatigue", "lethargy", "vomiting", "loss_of_appetite", "mild_fever", "headache"],
    "Impetigo": ["skin_rash", "itching", "fatigue", "high_fever", "blister", "red_sore_around_nose", "yellow_crust_ooze"],
    "Fungal Infection": ["itching", "skin_rash", "dischromic_patches", "nodal_skin_eruptions"],
    "Psoriasis": ["skin_rash", "joint_pain", "skin_peeling", "silver_like_dusting", "small_dents_in_nails"],
    "Acne": ["skin_rash", "pus_filled_pimples", "blackheads", "scurring"],
    "Arthritis": ["joint_pain", "swelling_joints", "knee_pain", "hip_joint_pain", "painful_walking", "fatigue"],
    "Varicose Veins": ["varicose_veins", "fatigue", "cramps", "swollen_legs", "prominent_veins_on_calf"],
    "Hypertension": ["headache", "chest_pain", "dizziness", "blurred_vision", "fatigue"],
    "Diabetes": ["fatigue", "weight_loss", "polyuria", "irregular_sugar_level", "excessive_hunger", "blurred_vision"],
    "GERD": ["acidity", "indigestion", "chest_pain", "vomiting", "cough", "stomach_pain"],
    "Peptic Ulcer Disease": ["vomiting", "indigestion", "loss_of_appetite", "abdominal_pain", "passage_of_gases"],
    "Drug Reaction": ["itching", "skin_rash", "stomach_pain", "vomiting", "burning_micturition"],
    "Urinary Tract Infection": ["burning_micturition", "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine"],
    "Cervical Spondylosis": ["back_pain", "weakness_in_limbs", "neck_pain", "dizziness", "movement_stiffness", "loss_of_balance"],
    "Dimorphic Hemorrhoids": ["constipation", "pain_in_anal_region", "bloody_stool", "irritation_in_anus", "pain_during_bowel_movements"],
    **_AUGMENT_PATTERNS,
}

_SYNTHETIC_SAMPLES_PER_DISEASE = 120


def build_synthetic_df() -> pd.DataFrame:
    """Full synthetic fallback dataset covering all diseases."""
    frames = [
        _generate_augmented(d, p, _SYNTHETIC_SAMPLES_PER_DISEASE)
        for d, p in _SYNTHETIC_PATTERNS.items()
    ]
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Training utilities
# ---------------------------------------------------------------------------

def _evaluate(model, name: str, X_test, y_test, classes: list[str]) -> dict:
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    logger.info("=== %s ===", name)
    logger.info("  Accuracy:   %.4f", acc)
    logger.info("  Precision:  %.4f", precision)
    logger.info("  Recall:     %.4f", recall)
    logger.info("  F1-score:   %.4f", f1)
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    print(f"  Accuracy:  {acc:.4f}  |  Precision: {precision:.4f}  |  Recall: {recall:.4f}  |  F1: {f1:.4f}")
    print(classification_report(y_test, y_pred, target_names=classes, zero_division=0, digits=4))
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


def _train_and_export(df: pd.DataFrame, source_label: str) -> None:
    """Core training routine — fits 3 models and exports them."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    available_cols = [c for c in SYMPTOM_LIST if c in df.columns]
    missing = len(SYMPTOM_LIST) - len(available_cols)
    if missing:
        logger.warning("%d symptom columns missing from dataset — padding with zeros.", missing)
    for col in SYMPTOM_LIST:
        if col not in df.columns:
            df[col] = 0

    X = df[SYMPTOM_LIST].values
    y = df["disease"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    classes = list(le.classes_)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc,
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print(f"\n[Training] Source: {source_label}  |  Samples: {len(df)}  |  Diseases: {len(classes)}")

    # Decision Tree
    dt = DecisionTreeClassifier(max_depth=12, min_samples_split=4, min_samples_leaf=2, random_state=42)
    dt.fit(X_train, y_train)
    dt_cv = cross_val_score(dt, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"\n  Decision Tree CV: {dt_cv.mean():.4f} ± {dt_cv.std():.4f}")
    _evaluate(dt, "Decision Tree", X_test, y_test, classes)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=150, max_depth=15, min_samples_split=4,
                                min_samples_leaf=2, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_cv = cross_val_score(rf, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"\n  Random Forest CV: {rf_cv.mean():.4f} ± {rf_cv.std():.4f}")
    _evaluate(rf, "Random Forest", X_test, y_test, classes)

    # Naive Bayes
    nb = GaussianNB()
    nb.fit(X_train, y_train)
    nb_cv = cross_val_score(nb, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"\n  Naive Bayes CV: {nb_cv.mean():.4f} ± {nb_cv.std():.4f}")
    _evaluate(nb, "Naive Bayes", X_test, y_test, classes)

    # Export
    joblib.dump(dt, MODEL_DIR / "decision_tree_v1.pkl")
    joblib.dump(rf, MODEL_DIR / "random_forest_v1.pkl")
    joblib.dump(nb, MODEL_DIR / "naive_bayes_v1.pkl")
    joblib.dump(le, MODEL_DIR / "label_encoder_v1.pkl")
    joblib.dump(SYMPTOM_LIST, MODEL_DIR / "symptom_columns_v1.pkl")

    print(f"\n{'='*60}")
    print(f"  TRAINING COMPLETE  ({source_label})")
    print(f"{'='*60}")
    print(f"  Models saved to : {MODEL_DIR}")
    print(f"  Diseases ({len(classes)}): {classes}")
    print(f"  Symptoms ({len(SYMPTOM_LIST)}): {len(SYMPTOM_LIST)} columns")
    print(f"  Total samples   : {len(df)}")


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def train_from_kaggle() -> None:
    """Primary path: Kaggle Symptom2Disease + emergency augmentation."""
    from ml.data.kaggle_pipeline import load_symptom2disease, save_processed

    kaggle_df = load_symptom2disease()
    save_processed(kaggle_df, "symptom2disease")

    augmented_df = build_augmented_df()
    df = pd.concat([kaggle_df, augmented_df], ignore_index=True)

    processed_dir = PROJECT_ROOT / "ml" / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_dir / "combined_dataset.csv", index=False)

    _train_and_export(df, "Kaggle Symptom2Disease + augmentation")


def train_synthetic_only() -> None:
    """Offline fallback: purely synthetic dataset."""
    df = build_synthetic_df()
    _train_and_export(df, "synthetic-only (offline fallback)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="SymptomScope AI — Model Training")
    parser.add_argument(
        "--synthetic-only", action="store_true",
        help="Skip Kaggle download and train on synthetic data only.",
    )
    args = parser.parse_args()

    if args.synthetic_only:
        print("Mode: synthetic-only")
        train_synthetic_only()
    else:
        print("Mode: Kaggle Symptom2Disease + emergency augmentation")
        try:
            train_from_kaggle()
        except Exception as exc:
            logger.warning("Kaggle download failed (%s). Falling back to synthetic data.", exc)
            print(f"\n[Warning] Kaggle failed ({exc}). Using synthetic fallback.\n")
            train_synthetic_only()


if __name__ == "__main__":
    main()
