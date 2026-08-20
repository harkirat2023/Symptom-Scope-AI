from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.v1.recovery import (
    _extract_json,
    _get_default_plan,
    _merge_plan_data,
    _prediction_context,
)
from repositories.recovery_repository import RecoveryPlanRepository
from schemas.prediction_schema import PredictionRecord


class TestExtractJson:
    def test_plain_json(self):
        raw = '{"a": 1, "b": [1, 2]}'
        assert _extract_json(raw) == {"a": 1, "b": [1, 2]}

    def test_fenced_json(self):
        raw = '```json\n{"a": 1}\n```'
        assert _extract_json(raw) == {"a": 1}

    def test_json_with_surrounding_text(self):
        raw = 'Sure, here is the plan:\n{"ok": true}\nHope that helps!'
        assert _extract_json(raw) == {"ok": True}

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            _extract_json("")

    def test_no_json_raises(self):
        with pytest.raises(ValueError):
            _extract_json("no json here")


class TestPredictionContext:
    def test_full_context(self):
        pred = PredictionRecord(
            _id="abc",
            user_id="u1",
            symptoms=["fever"],
            prediction="Influenza",
            confidence=85.5,
            severity="Moderate",
            timestamp="2026-01-01T00:00:00Z",
            age=30,
            gender="female",
            existing_conditions=["asthma"],
            symptom_duration="3 days",
            pain_level=4,
        )
        ctx = _prediction_context(pred)
        assert ctx["disease"] == "Influenza"
        assert ctx["age"] == 30
        assert ctx["gender"] == "female"
        assert ctx["existing_conditions"] == ["asthma"]
        assert ctx["symptom_duration"] == "3 days"
        assert ctx["pain_level"] == 4


class TestMergePlanData:
    def test_missing_keys_filled_from_defaults(self):
        context = {
            "disease": "Stroke",
            "confidence": 40.0,
            "severity": "Severe",
            "symptoms": ["fever"],
        }
        generated = {"what_it_means": "custom explanation"}
        merged = _merge_plan_data(generated, context)
        assert merged["what_it_means"] == "custom explanation"
        # Every section from the default plan is present
        for key in _get_default_plan(context):
            assert key in merged

    def test_empty_values_not_used(self):
        context = {"disease": "Flu", "confidence": 10, "severity": "Mild", "symptoms": []}
        generated = {"what_to_do": [], "foods_to_eat": None, "what_it_means": "  "}
        merged = _merge_plan_data(generated, context)
        defaults = _get_default_plan(context)
        assert merged["what_to_do"] == defaults["what_to_do"]
        assert merged["foods_to_eat"] == defaults["foods_to_eat"]


class TestRecoveryPlanRepository:
    def setup_method(self):
        self.repo = RecoveryPlanRepository()

    @pytest.mark.asyncio
    @patch("repositories.recovery_repository._get_collection")
    async def test_create(self, mock_get_collection):
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock()
        mock_collection.insert_one.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")
        mock_get_collection.return_value = mock_collection

        plan = await self.repo.create(
            user_id="u1",
            prediction_id="p1",
            disease="Stroke",
            confidence=42.45,
            severity="Severe",
            symptoms=["fever"],
            plan_data={"what_it_means": "x"},
        )
        assert plan["_id"] == "507f1f77bcf86cd799439011"
        assert plan["disease"] == "Stroke"
        assert plan["planData"] == {"what_it_means": "x"}
        assert plan["isRegenerated"] is False