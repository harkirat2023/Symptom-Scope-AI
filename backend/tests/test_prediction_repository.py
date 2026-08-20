from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from repositories.prediction_repository import PredictionRepository


class TestPredictionRepository:
    def setup_method(self):
        self.repo = PredictionRepository()

    @pytest.mark.asyncio
    @patch("repositories.prediction_repository._get_collection")
    async def test_create_prediction(self, mock_get_collection):
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock()
        mock_collection.insert_one.return_value = MagicMock(
            inserted_id="507f1f77bcf86cd799439011"
        )
        mock_get_collection.return_value = mock_collection

        result = await self.repo.create(
            user_id="user-1",
            symptoms=["fever", "cough"],
            prediction="Influenza",
            confidence=85.5,
            severity="Moderate",
        )

        assert result.id == "507f1f77bcf86cd799439011"
        assert result.user_id == "user-1"
        assert result.prediction == "Influenza"
        assert result.confidence == 85.5
        assert result.severity == "Moderate"
        assert result.symptoms == ["fever", "cough"]
        assert result.timestamp is not None

    @pytest.mark.asyncio
    @patch("repositories.prediction_repository._get_collection")
    async def test_find_by_user(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock()
        mock_cursor.to_list.return_value = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "userId": "user-1",
                "symptoms": ["fever"],
                "prediction": "Influenza",
                "confidence": 85.0,
                "severity": "Moderate",
                "timestamp": "2026-06-01T12:00:00+00:00",
            }
        ]
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        records = await self.repo.find_by_user("user-1")

        assert len(records) == 1
        assert records[0].user_id == "user-1"
        assert records[0].prediction == "Influenza"

    @pytest.mark.asyncio
    @patch("repositories.prediction_repository._get_collection")
    async def test_find_by_user_with_time_range(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock()
        mock_cursor.to_list.return_value = []
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        records = await self.repo.find_by_user("user-1", time_range="1m")

        mock_collection.find.assert_called_once()
        args = mock_collection.find.call_args
        query_arg = args[0][0] if args[0] else args[1]
        assert "userId" in query_arg
        assert "timestamp" in query_arg
        assert len(records) == 0

    @pytest.mark.asyncio
    @patch("repositories.prediction_repository._get_collection")
    async def test_find_by_user_empty(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock()
        mock_cursor.to_list.return_value = []
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        records = await self.repo.find_by_user("non-existent")
        assert len(records) == 0
