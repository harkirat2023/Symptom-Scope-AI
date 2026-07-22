"""
Kaggle Dataset Integration Pipeline.

Downloads and preprocesses medical symptom datasets from Kaggle
to augment the synthetic training data for improved model performance.

Supported datasets:
- "symptoms-checker" (Symptom Checker dataset)
- "disease-symptom-dataset" (Disease Symptom Prediction dataset)

Usage:
    python -m ml.data.kaggle_pipeline --dataset disease-symptom-dataset
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import kagglehub
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger("symptomscope.kaggle")

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "ml" / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "ml" / "data" / "processed"

SYMPTOM_COLUMNS = [
    "fever", "dry_cough", "fatigue", "headache", "sore_throat",
    "body_ache", "chest_pain", "shortness_of_breath", "nausea",
    "vomiting", "diarrhea", "loss_of_taste", "loss_of_smell",
    "runny_nose", "sneezing", "joint_pain", "chills", "sweating",
    "dizziness", "abdominal_pain", "rash", "muscle_weakness",
    "blurred_vision", "confusion", "seizure",
    "arm_pain", "jaw_pain", "facial_drooping", "speech_difficulty",
    "sensitivity_to_light", "sensitivity_to_sound",
]

DISEASE_MAPPING = {
    "Common Cold": "Common Cold",
    "Allergy": "Allergy",
    "Food Poisoning": "Mild Food Poisoning",
    "Influenza": "Influenza",
    "Bronchitis": "Bronchitis",
    "Gastroenteritis": "Gastroenteritis",
    "Migraine": "Migraine",
    "Pneumonia": "Pneumonia",
    "Heart Attack": "Heart Attack",
    "Stroke": "Stroke",
    "Malaria": "Malaria",
    "Dengue": "Dengue",
    "COVID-19": "COVID-19",
    "Epilepsy": "Epilepsy",
    "Hypertension": None,
    "Diabetes": None,
    "Asthma": None,
    "Tuberculosis": None,
    "Hepatitis B": None,
    "Hepatitis C": None,
    "Arthritis": None,
    "GERD": None,
    "Peptic ulcer diseae": None,
    "Hypothyroidism": None,
    "Hyperthyroidism": None,
    "Psoriasis": None,
    "Impetigo": None,
    "Fungal infection": None,
    "Drug Reaction": None,
}


def download_dataset(dataset_name: str) -> Optional[Path]:
    """Download a Kaggle dataset using kagglehub."""
    kaggle_paths = {
        "symptoms-checker": "symptoms-checker/symptom-checker-dataset",
        "disease-symptom-dataset": "kaushil268/disease-prediction-using-machine-learning",
    }
    path_str = kaggle_paths.get(dataset_name)
    if not path_str:
        logger.error("Unknown dataset: %s", dataset_name)
        return None
    logger.info("Downloading dataset: %s ...", path_str)
    try:
        download_path = Path(kagglehub.dataset_download(path_str))
        logger.info("Downloaded to: %s", download_path)
        return download_path
    except Exception as e:
        logger.warning("Kaggle download failed (%s). Using local file if available.", e)
        return None


def process_disease_symptom_dataset(download_path: Path) -> pd.DataFrame:
    """Process the Disease Symptom Prediction dataset into our format."""
    csv_files = list(download_path.glob("**/*.csv"))
    if not csv_files:
        logger.warning("No CSV files found in %s", download_path)
        return pd.DataFrame()

    df = pd.read_csv(csv_files[0])
    logger.info("Loaded dataset with shape: %s", df.shape)
    logger.info("Columns: %s", list(df.columns))

    records = []
    for _, row in df.iterrows():
        disease = str(row.get("Disease", "")).strip()
        mapped = DISEASE_MAPPING.get(disease)
        if mapped is None:
            continue
        symptoms_found = []
        for col in df.columns:
            if col == "Disease":
                continue
            val = str(row.get(col, "")).strip().lower()
            if val and val != "nan" and val != "":
                normalised = val.replace(" ", "_").replace("-", "_")
                if normalised in SYMPTOM_COLUMNS:
                    symptoms_found.append(normalised)
        if symptoms_found:
            features = [1 if s in symptoms_found else 0 for s in SYMPTOM_COLUMNS]
            records.append((features, mapped))

    result = pd.DataFrame([f for f, _ in records], columns=SYMPTOM_COLUMNS)
    result["disease"] = [d for _, d in records]
    logger.info("Processed %d records from Kaggle dataset", len(result))
    return result


def process_symptoms_checker_dataset(download_path: Path) -> pd.DataFrame:
    """Process the Symptom Checker dataset into our format."""
    csv_files = list(download_path.glob("**/*.csv"))
    if not csv_files:
        logger.warning("No CSV files found in %s", download_path)
        return pd.DataFrame()

    df = pd.read_csv(csv_files[0])
    logger.info("Loaded dataset with shape: %s", df.shape)

    records = []
    for _, row in df.iterrows():
        disease = str(row.get("label", row.get("disease", ""))).strip()
        mapped = DISEASE_MAPPING.get(disease)
        if mapped is None:
            continue
        symptom_cols = [c for c in df.columns if c.lower() != "label" and c.lower() != "disease"]
        symptoms_found = []
        for col in symptom_cols:
            val = str(row.get(col, "")).strip().lower()
            if val in ("1", "yes", "true"):
                normalised = col.replace(" ", "_").replace("-", "_").lower()
                if normalised in SYMPTOM_COLUMNS:
                    symptoms_found.append(normalised)
        if symptoms_found:
            features = [1 if s in symptoms_found else 0 for s in SYMPTOM_COLUMNS]
            records.append((features, mapped))

    result = pd.DataFrame([f for f, _ in records], columns=SYMPTOM_COLUMNS)
    result["disease"] = [d for _, d in records]
    logger.info("Processed %d records from Symptoms Checker dataset", len(result))
    return result


def merge_with_synthetic(kaggle_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Kaggle data with existing synthetic dataset."""
    synthetic_path = PROCESSED_DIR / "synthetic_dataset.csv"
    if not synthetic_path.exists():
        logger.info("No synthetic dataset found, using Kaggle data only")
        return kaggle_df

    synthetic_df = pd.read_csv(synthetic_path)
    logger.info("Loaded synthetic dataset with %d records", len(synthetic_df))

    combined = pd.concat([synthetic_df, kaggle_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=SYMPTOM_COLUMNS + ["disease"])
    logger.info("Combined dataset: %d records (after dedup)", len(combined))
    return combined


def main():
    parser = argparse.ArgumentParser(description="Kaggle Dataset Integration")
    parser.add_argument(
        "--dataset", type=str, default="disease-symptom-dataset",
        choices=["symptoms-checker", "disease-symptom-dataset"],
        help="Kaggle dataset name",
    )
    parser.add_argument(
        "--merge", action="store_true", default=True,
        help="Merge with synthetic dataset",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    download_path = download_dataset(args.dataset)
    if not download_path:
        logger.error("Failed to download dataset %s", args.dataset)
        sys.exit(1)

    if args.dataset == "disease-symptom-dataset":
        kaggle_df = process_disease_symptom_dataset(download_path)
    else:
        kaggle_df = process_symptoms_checker_dataset(download_path)

    if kaggle_df.empty:
        logger.warning("No usable records from Kaggle dataset")
        return

    output_path = PROCESSED_DIR / f"kaggle_{args.dataset.replace('-', '_')}.csv"
    kaggle_df.to_csv(output_path, index=False)
    logger.info("Saved Kaggle dataset to: %s", output_path)

    if args.merge:
        combined = merge_with_synthetic(kaggle_df)
        combined_path = PROCESSED_DIR / "combined_dataset.csv"
        combined.to_csv(combined_path, index=False)
        logger.info("Saved combined dataset to: %s", combined_path)
        logger.info("Total diseases: %d", combined["disease"].nunique())
        logger.info("Total samples: %d", len(combined))

    logger.info("Kaggle pipeline complete.")


if __name__ == "__main__":
    main()
