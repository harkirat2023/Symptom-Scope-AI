import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.agent_service import AgentService, WRITE_TOOLS


class TestParsePlan:
    def setup_method(self):
        self.agent = AgentService()

    def test_parse_plain(self):
        plan = self.agent._parse_plan('{"reply": "hi", "tool": null}')
        assert plan["reply"] == "hi"
        assert plan["tool"] is None

    def test_parse_fenced(self):
        plan = self.agent._parse_plan('```json\n{"reply": "hi", "tool": null}\n```')
        assert plan["reply"] == "hi"

    def test_parse_trailing_text(self):
        plan = self.agent._parse_plan('ok done\n{"reply": "y", "tool": null}\nthx')
        assert plan["reply"] == "y"

    def test_parse_invalid_raises(self):
        with pytest.raises(Exception):
            self.agent._parse_plan("no json")


class TestPlanNormalization:
    def setup_method(self):
        self.agent = AgentService()

    def _mock_llm(self, json_plan: str):
        llm = MagicMock()
        llm.invoke = AsyncMock(return_value=json_plan)
        self.agent.llm = llm

    @pytest.mark.asyncio
    @patch.object(AgentService, "_build_context", new_callable=AsyncMock)
    async def test_unknown_tool_is_dropped(self, mock_build_context):
        mock_build_context.return_value = "ctx"
        self._mock_llm(
            '{"reply": "hello", "tool": {"name": "delete_database", "args": {}}, "action_summary": "", "confirm_required": true}'
        )
        reply, pending = await self.agent.run_turn(
            "u1", "s1", "hello", [], None
        )
        assert pending is None
        assert reply == "hello"

    @pytest.mark.asyncio
    @patch.object(AgentService, "_build_context", new_callable=AsyncMock)
    @patch("repositories.agent_repository.PendingActionRepository.create", new_callable=AsyncMock)
    @patch("repositories.agent_repository.PendingActionRepository.expire_stale", new_callable=AsyncMock)
    async def test_write_tool_forces_confirmation(
        self, mock_expire, mock_create, mock_build_context
    ):
        mock_build_context.return_value = "ctx"
        # Model says confirm_required=false — backend must force it for write tools.
        self._mock_llm(
            '{"reply": "I can do that", "tool": {"name": "create_reminder", "args": {"medicine_name": "Metformin"}}, "action_summary": "Create reminder", "confirm_required": false}'
        )
        mock_create.return_value = {
            "_id": "act123",
            "sessionId": "s1",
            "tool": "create_reminder",
            "args": {"medicine_name": "Metformin"},
            "summary": "Create reminder",
            "status": "pending",
            "createdAt": "2026-01-01T00:00:00Z",
            "expiresAt": "2026-01-02T00:00:00Z",
        }
        reply, pending = await self.agent.run_turn("u1", "s1", "remind me", [], None)
        assert pending is not None
        assert pending.id == "act123"
        assert pending.tool == "create_reminder"
        assert mock_create.await_count == 1

    @pytest.mark.asyncio
    @patch.object(AgentService, "_build_context", new_callable=AsyncMock)
    @patch.object(AgentService, "_execute_tool", new_callable=AsyncMock)
    @patch.object(AgentService, "_finalize", new_callable=AsyncMock)
    async def test_read_tool_runs_immediately(
        self, mock_finalize, mock_execute, mock_build_context
    ):
        mock_build_context.return_value = "ctx"
        self._mock_llm(
            '{"reply": "checking", "tool": {"name": "get_profile", "args": {}}, "action_summary": "", "confirm_required": false}'
        )
        mock_execute.return_value = {"profile": {"email": "a@b.com"}}
        mock_finalize.return_value = "Here is your profile."
        reply, pending = await self.agent.run_turn("u1", "s1", "profile", [], None)
        assert pending is None
        assert reply == "Here is your profile."
        mock_execute.assert_awaited_once_with("u1", "get_profile", {})

    @pytest.mark.asyncio
    @patch("repositories.agent_repository.PendingActionRepository.find_by_id", new_callable=AsyncMock)
    @patch.object(AgentService, "_execute_tool", new_callable=AsyncMock)
    @patch.object(AgentService, "_finalize", new_callable=AsyncMock)
    @patch("repositories.agent_repository.PendingActionRepository.mark_resolved", new_callable=AsyncMock)
    async def test_confirm_approve_executes(
        self, mock_mark, mock_finalize, mock_execute, mock_find
    ):
        mock_find.return_value = {
            "userId": "u1",
            "tool": "update_profile",
            "args": {"email": "a@b.com"},
            "status": "pending",
            "expiresAt": "2099-01-01T00:00:00Z",
        }
        mock_execute.return_value = {"profile": {"email": "a@b.com"}}
        mock_finalize.return_value = "Profile updated."
        reply, pending = await self.agent.confirm_action("u1", "act1", "approve")
        assert reply == "Profile updated."
        mock_execute.assert_awaited_once_with("u1", "update_profile", {"email": "a@b.com"})

    @pytest.mark.asyncio
    @patch("repositories.agent_repository.PendingActionRepository.find_by_id", new_callable=AsyncMock)
    @patch("repositories.agent_repository.PendingActionRepository.mark_resolved", new_callable=AsyncMock)
    async def test_confirm_decline_does_not_execute(self, mock_mark, mock_find):
        mock_find.return_value = {
            "userId": "u1",
            "tool": "delete_reminder",
            "args": {"reminder_id": "r1"},
            "status": "pending",
            "expiresAt": "2099-01-01T00:00:00Z",
        }
        with patch.object(AgentService, "_execute_tool", new_callable=AsyncMock) as mock_exec:
            reply, pending = await self.agent.confirm_action("u1", "act1", "decline")
        mock_exec.assert_not_awaited()
        assert "won't" in reply.lower()


class TestToolRegistry:
    def test_write_tools_exist_in_descriptions(self):
        from services.agent_service import TOOL_DESCRIPTIONS
        for tool in WRITE_TOOLS:
            assert tool in TOOL_DESCRIPTIONS

    @pytest.mark.asyncio
    async def test_execute_unknown_tool_raises(self):
        agent = AgentService()
        with pytest.raises(ValueError):
            await agent._execute_tool("u1", "does_not_exist", {})