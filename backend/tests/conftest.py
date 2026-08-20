import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Tests never touch a real MongoDB server: point the client at a non-routable
# local URI so pymongo's background monitor threads do not attempt an SSL
# handshake against a live Atlas cluster (which can hang or crash on some
# Python/OpenSSL builds). All DB access in tests is mocked.
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test")

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from auth.dependency import get_current_user
from main import app

# ── Test doctor data (availability as list[str]) ──────────────────────
_MOCK_DOCTORS = [
    {"name": "Dr. Sharma", "specialty": "General Physician", "location": "Ludhiana", "rating": 4.5, "distance_km": 2.3, "availability": ["Today"], "phone": "+91-161-XXXXXXX", "hospital": "Dayanand Medical College", "experience_years": 15, "createdAt": datetime.now(UTC).isoformat()},
    {"name": "Dr. Patel", "specialty": "Cardiologist", "location": "Amritsar", "rating": 4.7, "distance_km": 5.0, "availability": ["Today"], "phone": "+91-183-XXXXXXX", "hospital": "Apollo Amritsar", "experience_years": 18, "createdAt": datetime.now(UTC).isoformat()},
    {"name": "Dr. Mehta", "specialty": "Cardiologist", "location": "Ludhiana", "rating": 4.9, "distance_km": 2.0, "availability": ["Today"], "phone": "+91-161-XXXXXX4", "hospital": "Dayanand Medical College", "experience_years": 25, "createdAt": datetime.now(UTC).isoformat()},
]

_MOCK_SPECIALTIES = ["General Physician", "Cardiologist", "Neurologist"]
_MOCK_LOCATIONS = ["Ludhiana", "Amritsar", "Patiala", "Jalandhar"]

# ── Test hospital data ───────────────────────────────────────────────
_MOCK_HOSPITALS = [
    {"name": "CMC Ludhiana", "location": "Ludhiana", "specialties": ["Cardiology", "Neurology"], "rating": 4.8, "distance_km": 3.0, "phone": "+91-161-5032255", "has_emergency": True, "has_ambulance": True, "bed_count": 1800, "address": "Brown Road, Ludhiana"},
    {"name": "Apollo Amritsar", "location": "Amritsar", "specialties": ["Cardiology", "Neurology"], "rating": 4.7, "distance_km": 2.1, "phone": "+91-183-5088888", "has_emergency": True, "has_ambulance": True, "bed_count": 500, "address": "Queens Road, Amritsar"},
    {"name": "Surya Hospital", "location": "Amritsar", "specialties": ["General Medicine"], "rating": 4.2, "distance_km": 1.8, "phone": "+91-183-5012345", "has_emergency": False, "has_ambulance": False, "bed_count": 150, "address": "Mall Road, Amritsar"},
]
_MOCK_HOSPITAL_LOCATIONS = ["Ludhiana", "Amritsar", "Patiala", "Jalandhar"]


def _make_mock_cursor(data: list[dict]) -> MagicMock:
    """Return a chainable cursor mock whose .to_list() returns *data*."""
    c = MagicMock()
    c.sort.return_value = c
    c.limit.return_value = c
    c.to_list = AsyncMock(return_value=data)
    c.__aiter__.return_value = iter(data)
    return c


def _mock_find(data: list[dict]):
    """Return a function suitable as a mock side_effect for col.find().

    Applies simple $regex and equality filtering so filtered queries behave realistically.
    """
    import re as _re

    def find(filter_dict: dict | None = None, **kwargs) -> MagicMock:
        result = list(data)
        if filter_dict:
            for field, condition in filter_dict.items():
                if isinstance(condition, dict) and "$regex" in condition:
                    pattern = condition["$regex"]
                    opts = condition.get("$options", "")
                    flags = 0
                    if "i" in opts:
                        flags = _re.IGNORECASE
                    result = [d for d in result if _re.search(pattern, str(d.get(field, "")), flags)]
                else:
                    # simple equality
                    result = [d for d in result if d.get(field) == condition]
        return _make_mock_cursor(result)
    return find


def _make_mock_collection(data: list[dict]) -> MagicMock:
    """Build a mock MongoDB collection with common methods."""
    col = AsyncMock()
    col.insert_one = AsyncMock()
    col.insert_many = AsyncMock()
    col.count_documents = AsyncMock(return_value=len(data))
    col.find = MagicMock(side_effect=_mock_find(data))
    col.sort = MagicMock(return_value=col)
    col.limit = MagicMock(return_value=col)
    return col


@pytest.fixture(autouse=True)
def _mock_mongodb_lifespan():
    """Patch the lifespan's ensure_indexes to avoid Motor event loop issues."""
    with (
        patch("main.ensure_indexes", new_callable=AsyncMock),
        patch("services.rag_service.RAGService.has_documents", return_value=False),
        patch("services.rag_service.RAGService.initialize_knowledge_base", return_value=0),
        patch("services.reminder_service.scheduler.start", new_callable=AsyncMock),
        patch("services.reminder_service.scheduler.stop", new_callable=AsyncMock),
    ):
        yield


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: "test-user-id"

    doctor_col = _make_mock_collection(_MOCK_DOCTORS)
    doctor_col.distinct = AsyncMock(side_effect=lambda field: {
        "specialty": _MOCK_SPECIALTIES,
        "location": _MOCK_LOCATIONS,
    }.get(field, []))

    hospital_col = _make_mock_collection(_MOCK_HOSPITALS)
    hospital_col.distinct = AsyncMock(return_value=_MOCK_HOSPITAL_LOCATIONS)

    prediction_col = _make_mock_collection([])
    prediction_col.insert_one = AsyncMock(return_value=MagicMock(inserted_id="507f1f77bcf86cd799439011"))
    prediction_col.find = MagicMock(return_value=_make_mock_cursor([]))

    with (
        patch("repositories.doctor_repository._get_collection", return_value=doctor_col),
        patch("repositories.hospital_repository._get_collection", return_value=hospital_col),
        patch("repositories.prediction_repository._get_collection", return_value=prediction_col),
        TestClient(app) as test_client,
    ):
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_db():
    with patch("repositories.prediction_repository._get_collection") as mock:
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock()

        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])

        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock.return_value = mock_collection
        yield mock_collection
