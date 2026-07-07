import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from auth.dependency import get_current_user


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: "test-user-id"
    with TestClient(app) as test_client:
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
