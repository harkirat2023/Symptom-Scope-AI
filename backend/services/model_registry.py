"""Shared singleton for loading and caching ML model artifacts."""

import joblib
import numpy as np
from pathlib import Path
from threading import Lock

_models_path = Path(__file__).parent.parent / "ml" / "models"

_cache: dict[str, object] = {}
_cache_lock = Lock()


def _get_model(name: str) -> object:
    with _cache_lock:
        if name not in _cache:
            _cache[name] = joblib.load(_models_path / name)
        return _cache[name]


def get_decision_tree():
    return _get_model("decision_tree_v1.pkl")


def get_random_forest():
    return _get_model("random_forest_v1.pkl")


def get_naive_bayes():
    return _get_model("naive_bayes_v1.pkl")


def get_label_encoder():
    return _get_model("label_encoder_v1.pkl")


def get_symptom_columns() -> list[str]:
    result = _get_model("symptom_columns_v1.pkl")
    assert isinstance(result, list)
    return result


def get_rf_feature_importances() -> np.ndarray:
    rf = get_random_forest()
    return rf.feature_importances_


def clear_cache():
    """Clear the model cache (useful for testing)."""
    with _cache_lock:
        _cache.clear()
