"""
ml.data.download_kaggle
========================
Quick helper to pre-download the Symptom2Disease dataset to the local cache.

Usage:
    python -m ml.data.download_kaggle
"""

from pathlib import Path


def download_dataset() -> Path:
    try:
        import kagglehub
    except ImportError:
        raise ImportError("kagglehub is required. Install with: pip install 'kagglehub[pandas-datasets]'")

    print("Downloading niyarrbarman/symptom2disease from Kaggle …")
    path = kagglehub.dataset_download("niyarrbarman/symptom2disease")
    dest = Path(path)
    print(f"Dataset cached at: {dest}")
    return dest


if __name__ == "__main__":
    download_dataset()
