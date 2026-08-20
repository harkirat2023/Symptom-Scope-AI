"""
ml.data.kaggle_pipeline
=======================
Loads the Symptom2Disease Kaggle dataset and converts its natural-language
symptom descriptions into binary feature vectors compatible with the
SymptomScope AI training pipeline.

Dataset: niyarrbarman/symptom2disease
  - 1,200 rows  |  columns: label (disease), text (free-text symptoms)
  - 24 diseases × 50 samples each

Usage:
    python -m ml.data.kaggle_pipeline
"""
import logging
from pathlib import Path

import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

from ml.constants import SYMPTOM_LIST

logger = logging.getLogger("symptomscope.kaggle_pipeline")

PROJECT_ROOT = Path(__file__).parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "ml" / "data" / "processed"

# ---------------------------------------------------------------------------
# Canonical disease names (Kaggle label → internal name)
# ---------------------------------------------------------------------------
DISEASE_LABEL_MAP: dict[str, str] = {
    # Already present in registry
    "Psoriasis": "Psoriasis",
    "Varicose Veins": "Varicose Veins",
    "Typhoid": "Typhoid",
    "Chicken pox": "Chicken Pox",
    "Impetigo": "Impetigo",
    "Dengue": "Dengue",
    "Fungal infection": "Fungal Infection",
    "Common Cold": "Common Cold",
    "Pneumonia": "Pneumonia",
    "Dimorphic hemmorhoids(piles)": "Dimorphic Hemorrhoids",
    "Arthritis": "Arthritis",
    "Acne": "Acne",
    "Bronchial Asthma": "Bronchial Asthma",
    "Hypertension ": "Hypertension",
    "Hypertension": "Hypertension",
    "Migraine": "Migraine",
    "Cervical spondylosis": "Cervical Spondylosis",
    "Jaundice": "Jaundice",
    "Malaria": "Malaria",
    "urinary tract infection": "Urinary Tract Infection",
    "Allergy": "Allergy",
    "gastroesophageal reflux disease": "GERD",
    "drug reaction": "Drug Reaction",
    "peptic ulcer diseae": "Peptic Ulcer Disease",
    "Diabetes ": "Diabetes",
    "Diabetes": "Diabetes",
}

# ---------------------------------------------------------------------------
# Keyword → canonical symptom mapping
# Each entry maps a phrase (found in symptom text) to a SYMPTOM_LIST column.
# Longer / more-specific phrases come first so they match before shorter ones.
# ---------------------------------------------------------------------------
KEYWORD_MAP: dict[str, str] = {
    # Skin
    "silver like dusting": "silver_like_dusting",
    "small dents in nails": "small_dents_in_nails",
    "inflammatory nails": "inflammatory_nails",
    "skin peeling": "skin_peeling",
    "pus filled pimples": "pus_filled_pimples",
    "red sore around nose": "red_sore_around_nose",
    "yellow crust ooze": "yellow_crust_ooze",
    "dischromic patches": "dischromic_patches",
    "nodal skin eruptions": "nodal_skin_eruptions",
    "skin rash": "skin_rash",
    "blackheads": "blackheads",
    "scurring": "scurring",
    "blister": "blister",
    "itching": "itching",
    "rash": "rash",
    # Vascular / legs
    "prominent veins on calf": "prominent_veins_on_calf",
    "swollen blood vessels": "swollen_blood_vessels",
    "varicose veins": "varicose_veins",
    "swollen legs": "swollen_legs",
    "painful walking": "painful_walking",
    "cramps": "cramps",
    # Gastrointestinal
    "pain during bowel movements": "pain_during_bowel_movements",
    "pain in anal region": "pain_in_anal_region",
    "irritation in anus": "irritation_in_anus",
    "bloody stool": "bloody_stool",
    "loss of appetite": "loss_of_appetite",
    "passage of gases": "passage_of_gases",
    "internal itching": "internal_itching",
    "distention of abdomen": "distention_of_abdomen",
    "swelling of stomach": "swelling_of_stomach",
    "stomach pain": "stomach_pain",
    "abdominal pain": "abdominal_pain",
    "belly pain": "belly_pain",
    "indigestion": "indigestion",
    "acidity": "acidity",
    "constipation": "constipation",
    "diarrhea": "diarrhea",
    "nausea": "nausea",
    "vomiting": "vomiting",
    # Urinary
    "continuous feel of urine": "continuous_feel_of_urine",
    "bladder discomfort": "bladder_discomfort",
    "foul smell of urine": "foul_smell_of_urine",
    "burning micturition": "burning_micturition",
    "spotting urination": "spotting_urination",
    "dark urine": "dark_urine",
    "yellow urine": "yellow_urine",
    # Liver / jaundice
    "yellowing of eyes": "yellowing_of_eyes",
    "yellowish skin": "yellowish_skin",
    "acute liver failure": "acute_liver_failure",
    "stomach bleeding": "stomach_bleeding",
    "fluid overload": "fluid_overload",
    # Neurological
    "weakness in limbs": "weakness_in_limbs",
    "movement stiffness": "movement_stiffness",
    "spinning movements": "spinning_movements",
    "visual disturbances": "visual_disturbances",
    "loss of balance": "loss_of_balance",
    "unsteadiness": "unsteadiness",
    "altered sensorium": "altered_sensorium",
    "slurred speech": "slurred_speech",
    "speech difficulty": "speech_difficulty",
    "facial drooping": "facial_drooping",
    "stiff neck": "stiff_neck",
    "neck pain": "neck_pain",
    "back pain": "back_pain",
    "muscle weakness": "muscle_weakness",
    "muscle pain": "muscle_pain",
    "blurred vision": "blurred_vision",
    "confusion": "confusion",
    "seizure": "seizure",
    "headache": "headache",
    "dizziness": "dizziness",
    "anxiety": "anxiety",
    # Joints / musculoskeletal
    "swelling joints": "swelling_joints",
    "hip joint pain": "hip_joint_pain",
    "knee pain": "knee_pain",
    "joint pain": "joint_pain",
    "swollen extremeties": "swollen_extremeties",
    # Respiratory
    "shortness of breath": "shortness_of_breath",
    "breathlessness": "breathlessness",
    "blood in sputum": "blood_in_sputum",
    "mucoid sputum": "mucoid_sputum",
    "rusty sputum": "rusty_sputum",
    "throat irritation": "throat_irritation",
    "patches in throat": "patches_in_throat",
    "redness of eyes": "redness_of_eyes",
    "watering from eyes": "watering_from_eyes",
    "sinus pressure": "sinus_pressure",
    "chest pain": "chest_pain",
    "sore throat": "sore_throat",
    "runny nose": "runny_nose",
    "phlegm": "phlegm",
    "cough": "cough",
    "sneezing": "sneezing",
    "congestion": "congestion",
    # Fever / systemic
    "high fever": "high_fever",
    "mild fever": "mild_fever",
    "sweating": "sweating",
    "chills": "chills",
    "fever": "fever",
    "fatigue": "fatigue",
    "malaise": "malaise",
    "lethargy": "lethargy",
    "dehydration": "dehydration",
    "body ache": "body_ache",
    # Metabolic / endocrine
    "irregular sugar level": "irregular_sugar_level",
    "excessive hunger": "excessive_hunger",
    "increased appetite": "increased_appetite",
    "weight gain": "weight_gain",
    "weight loss": "weight_loss",
    "polyuria": "polyuria",
    "obesity": "obesity",
    "puffy face and eyes": "puffy_face_and_eyes",
    "sunken eyes": "sunken_eyes",
    "enlarged thyroid": "enlarged_thyroid",
    "brittle nails": "brittle_nails",
    "excessive sweating": "excessive_sweating",
    "cold hands and feets": "cold_hands_and_feets",
    "mood swings": "mood_swings",
    "palpitations": "palpitations",
    "family history": "family_history",
    # Haematological
    "bruising": "bruising",
    "swollen lymph nodes": "swollen_lymph_nodes",
    "red spots over body": "red_spots_over_body",
    "abnormal menstruation": "abnormal_menstruation",
    "receiving blood transfusion": "receiving_blood_transfusion",
    "history of alcohol consumption": "history_of_alcohol_consumption",
    # Sensory
    "loss of taste": "loss_of_taste",
    "loss of smell": "loss_of_smell",
    "sensitivity to light": "sensitivity_to_light",
    "sensitivity to sound": "sensitivity_to_sound",
    # Emergency / cardiac
    "arm pain": "arm_pain",
    "jaw pain": "jaw_pain",
    # Misc
    "toxic look": "toxic_look_typhos",
    "continuous sneezing": "continuous_sneezing",
}

# Sort by length (descending) so longer phrases are matched first
_SORTED_KEYWORDS: list[tuple[str, str]] = sorted(
    KEYWORD_MAP.items(), key=lambda kv: len(kv[0]), reverse=True
)

_SYMPTOM_SET = set(SYMPTOM_LIST)


def text_to_binary_features(text: str) -> dict[str, int]:
    """Convert a free-text symptom description into a binary feature dict."""
    text_lower = text.lower()
    found: set[str] = set()
    for phrase, column in _SORTED_KEYWORDS:
        if phrase in text_lower and column in _SYMPTOM_SET:
            found.add(column)
    return {s: (1 if s in found else 0) for s in SYMPTOM_LIST}


def load_symptom2disease() -> pd.DataFrame:
    """
    Download and convert the Symptom2Disease dataset to binary feature format.

    Returns a DataFrame with columns = SYMPTOM_LIST + ["disease"].
    """
    logger.info("Loading niyarrbarman/symptom2disease via kagglehub …")
    # The dataset contains a single CSV file named 'Symptom2Disease.csv'
    raw: pd.DataFrame = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "niyarrbarman/symptom2disease",
        "Symptom2Disease.csv",
    )
    logger.info("Raw dataset shape: %s | columns: %s", raw.shape, list(raw.columns))

    # Normalize column names
    raw.columns = [c.strip().lower() for c in raw.columns]
    label_col = "label" if "label" in raw.columns else raw.columns[0]
    text_col = "text" if "text" in raw.columns else raw.columns[1]

    records: list[dict] = []
    skipped = 0
    for _, row in raw.iterrows():
        raw_label = str(row[label_col]).strip()
        canonical = DISEASE_LABEL_MAP.get(raw_label)
        if canonical is None:
            skipped += 1
            continue
        features = text_to_binary_features(str(row[text_col]))
        features["disease"] = canonical
        records.append(features)

    logger.info(
        "Converted %d records (%d skipped / unmapped labels).", len(records), skipped
    )
    df = pd.DataFrame(records)
    # Ensure all SYMPTOM_LIST columns exist (in correct order)
    for col in SYMPTOM_LIST:
        if col not in df.columns:
            df[col] = 0
    df = df[SYMPTOM_LIST + ["disease"]]
    return df


def save_processed(df: pd.DataFrame, name: str = "symptom2disease") -> Path:
    """Save a processed DataFrame to the processed/ directory."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    logger.info("Saved processed dataset → %s  (%d rows)", path, len(df))
    return path


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    df = load_symptom2disease()
    path = save_processed(df)
    print(f"\nDone. Processed dataset: {path}")
    print(f"Shape: {df.shape}")
    print(f"Diseases ({df['disease'].nunique()}): {sorted(df['disease'].unique())}")
    coverage = (df[SYMPTOM_LIST] > 0).sum()
    active = coverage[coverage > 0]
    print(f"\nActive symptoms ({len(active)}/{len(SYMPTOM_LIST)}):")
    print(active.sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
