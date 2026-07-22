"""
Download the Kaggle Disease Symptom Description Dataset.

Usage:
    python -m ml.data.download_kaggle

Requires: kagglehub (pip install kagglehub)
"""

from pathlib import Path


def download_dataset() -> Path:
    try:
        import kagglehub
    except ImportError:
        raise ImportError("kagglehub is required. Install with: pip install kagglehub")

    print("Downloading disease-symptom-description-dataset from Kaggle...")
    path = kagglehub.dataset_download("itachi9604/disease-symptom-description-dataset")
    dest = Path(path)
    print(f"Dataset downloaded to: {dest}")

    raw_dir = Path(__file__).parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for f in dest.glob("*"):
        target = raw_dir / f.name
        if not target.exists():
            import shutil
            shutil.copy2(f, target)
            print(f"  Copied: {f.name} -> {target}")

    print(f"Raw dataset stored in: {raw_dir}")
    return raw_dir


if __name__ == "__main__":
    download_dataset()
