"""
Goal-driven Health Assistant agent.

The assistant is a goal-driven AI agent that:
1. Guides the user toward a diagnosis, recovery plan, and email reminders.
2. Uses tools (symptom/prediction context, recovery plan, reminders,
   profile/email, RAG medical QA) to act on the user's behalf.
3. Requires explicit user confirmation for EVERY write operation
   (create/update/delete reminders, generating a recovery plan,
   updating the profile). Read-only tools run automatically.

Architecture (per user message):
  plan  ->  if write tool -> create pending action + ask for confirmation
         -> if read tool  -> execute -> finalize reply
  confirm -> execute stored action -> finalize reply
"""

import json
import logging
from datetime import UTC, datetime

from schemas.chat_schema import PendingActionResponse

_logger = logging.getLogger("symptomscope.agent")

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

WRITE_TOOLS = {
    "update_profile",
    "generate_recovery_plan",
    "create_reminder",
    "update_reminder",
    "delete_reminder",
}

TOOL_DESCRIPTIONS = {
    "get_profile": {
        "type": "read",
        "description": "Return the user's health profile (email, location, health goals).",
    },
    "update_profile": {
        "type": "write",
        "description": "Save or update the user's email, location, or health goals. Requires confirmation.",
        "args": {
            "email": "string, optional, user's email address for reminders",
            "location": "string, optional, city/region for local care",
            "health_goals": "list of strings, optional, e.g. ['lower blood pressure']",
        },
    },
    "get_recovery_plan": {
        "type": "read",
        "description": "Return the user's latest recovery plan.",
    },
    "generate_recovery_plan": {
        "type": "write",
        "description": "Generate a personalized recovery plan from the user's latest prediction. Requires confirmation.",
        "args": {"prediction_id": "string, optional, defaults to latest prediction"},
    },
    "get_reminders": {
        "type": "read",
        "description": "List the user's medication reminders.",
    },
    "create_reminder": {
        "type": "write",
        "description": "Create a new medication reminder. Requires confirmation.",
        "args": {
            "medicine_name": "string, required",
            "dosage": "string, required",
            "frequency": "string 'daily' or 'specific_days', required",
            "schedule_details": "object, optional, e.g. {'times': ['08:00']}",
            "duration_days": "integer, optional, default 7",
            "start_time": "string 'HH:MM', required",
            "email_reminder": "boolean, optional, default false",
        },
    },
    "update_reminder": {
        "type": "write",
        "description": "Update an existing medication reminder. Requires confirmation.",
        "args": {
            "reminder_id": "string, required",
            "medicine_name": "string, optional",
            "dosage": "string, optional",
            "start_time": "string, optional",
            "status": "string, optional (active/paused/completed)",
        },
    },
    "delete_reminder": {
        "type": "write",
        "description": "Delete a medication reminder. Requires confirmation.",
        "args": {"reminder_id": "string, required"},
    },
    "get_predictions": {
        "type": "read",
        "description": "List the user's symptom check history (predictions).",
    },
    "ask_medical": {
        "type": "read",
        "description": "Answer a general medical question using the knowledge base.",
        "args": {"query": "string, required"},
    },
}

AGENT_SYSTEM_PROMPT = """You are the SymptomScope Health Assistant, a goal-driven AI agent that helps the user take control of their health.

YOUR GOALS (in priority order):
1. Help the user understand their predicted condition and get a personalized recovery plan.
2. Help the user set up medication reminders and enable email reminders.
3. Answer medical questions using only the provided context (educational only).

You NEVER diagnose, prescribe, or replace professional medical advice. You always include a short educational disclaimer in final answers.

TOOLS — you may use EXACTLY ONE tool per turn. Choose a tool only when it clearly helps reach a goal. Available tools:
{descriptions}

INSTRUCTIONS:
- Respond to the user in a warm, concise, human tone (2-4 sentences).
- If the user asks for or implies an action (e.g. "remind me", "save my email", "make a plan", "change the reminder"), pick the matching tool and set confirm_required to true.
- For read-only tools set confirm_required to false.
- Do NOT invent facts about the user. Use the provided context.
- If the user's message is a follow-up ("yes", "no", "ok", "go ahead") referring to an offer you made, set "tool" to null and acknowledge; the confirmation flow is handled separately.
- If no tool is needed, set tool to null.

CURRENT STATE:
{context}

CONVERSATION SO FAR (recent):
{history}

USER: {message}

Respond with a single JSON object only:
{{
  "reply": "your conversational reply to the user",
  "tool": null or {{"name": "tool_name", "args": {{...}}}},
  "action_summary": "short human-readable summary of the action (for a confirmation card)",
  "confirm_required": true or false
}}
"""

FINALIZE_PROMPT = """You are the SymptomScope Health Assistant. Summarize the result of the action that was just completed for the user.

ACTION PERFORMED:
{tool_summary}

RESULT:
{result}

Write a warm, concise reply (2-4 sentences) telling the user what was done and any next step. Include a short educational disclaimer where relevant. Do not invent extra facts."""


def _read_tools() -> str:
    lines = []
    for name, spec in TOOL_DESCRIPTIONS.items():
        args = spec.get("args")
        args_txt = ""
        if args:
            args_txt = " | args: " + ", ".join(f"{k}: {v}" for k, v in args.items())
        lines.append(f"- {name} ({spec['type']}): {spec['description']}{args_txt}")
    return "\n".join(lines)


class AgentService:
    def __init__(self):
        from services.llm_service import LLMService
        self.llm = LLMService()

    # ------------------------------------------------------------------
    # Context building
    # ------------------------------------------------------------------

    async def _build_context(self, user_id: str, session_prediction_context: dict | None) -> str:
        from repositories.agent_repository import ProfileRepository
        from repositories.prediction_repository import PredictionRepository
        from repositories.recovery_repository import RecoveryPlanRepository
        from repositories.reminder_repository import ReminderRepository

        profile = await ProfileRepository().get(user_id)
        latest_pred = await PredictionRepository().find_latest_by_user(user_id)
        plan = await RecoveryPlanRepository().find_latest_by_user(user_id)
        reminders = await ReminderRepository().find_by_user(user_id, limit=5)

        parts = []
        parts.append("-- USER PROFILE --")
        if profile:
            parts.append(
                f"email: {profile.get('email') or 'not set'}; "
                f"location: {profile.get('location') or 'not set'}; "
                f"health goals: {', '.join(profile.get('health_goals', [])) or 'none'}"
            )
        else:
            parts.append("No profile saved yet.")

        parts.append("-- LATEST PREDICTION --")
        if latest_pred:
            parts.append(
                f"disease: {latest_pred.prediction}; confidence: "
                f"{latest_pred.confidence}%; severity: {latest_pred.severity}; "
                f"symptoms: {', '.join(latest_pred.symptoms) or 'n/a'}"
            )
        else:
            parts.append("No symptom check performed yet.")

        parts.append("-- RECOVERY PLAN --")
        if plan:
            pd = plan.get("planData", {})
            parts.append(
                f"exists (created {plan.get('createdAt', 'unknown')}); "
                f"what_it_means: {str(pd.get('what_it_means'))[:200]}"
            )
        else:
            parts.append("No recovery plan yet.")

        parts.append("-- MEDICATION REMINDERS --")
        if reminders:
            for r in reminders:
                parts.append(
                    f"- {r.get('medicine_name')} {r.get('dosage')} "
                    f"({r.get('status')}, email={r.get('email_reminder', False)})"
                )
        else:
            parts.append("No reminders set up.")

        parts.append("-- SESSION PREDICTION CONTEXT --")
        if session_prediction_context:
            parts.append(
                f"disease: {session_prediction_context.get('disease')}; "
                f"confidence: {session_prediction_context.get('confidence')}; "
                f"severity: {session_prediction_context.get('severity')}"
            )
        else:
            parts.append("None.")

        # Goal status (drives the agent's behavior)
        parts.append("-- GOAL STATUS --")
        if not profile:
            parts.append("1. Collect email + location (for reminders and local care).")
        else:
            parts.append("1. Email + location collected.")
        if not latest_pred:
            parts.append("2. User should run a symptom check.")
        elif not plan:
            parts.append("2. Generate the user's recovery plan.")
        else:
            parts.append("2. Recovery plan exists.")
        if not reminders:
            parts.append("3. Set up medication reminders + email alerts.")
        else:
            parts.append("3. Reminders configured.")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    async def _execute_tool(self, user_id: str, name: str, args: dict) -> dict:
        handler = getattr(self, f"_tool_{name}", None)
        if handler is None:
            raise ValueError(f"Unknown tool: {name}")
        return await handler(user_id, args)

    async def _tool_get_profile(self, user_id: str, args: dict) -> dict:
        from repositories.agent_repository import ProfileRepository
        profile = await ProfileRepository().get(user_id)
        return {"profile": profile or {}}

    async def _tool_update_profile(self, user_id: str, args: dict) -> dict:
        from repositories.agent_repository import ProfileRepository
        allowed = {k: args[k] for k in ("email", "location", "health_goals") if k in args}
        if not allowed:
            raise ValueError("Nothing to update in profile")
        profile = await ProfileRepository().upsert(user_id, allowed)
        return {"profile": profile or {}, "updated": allowed}

    async def _tool_get_recovery_plan(self, user_id: str, args: dict) -> dict:
        from repositories.recovery_repository import RecoveryPlanRepository
        plan = await RecoveryPlanRepository().find_latest_by_user(user_id)
        if not plan:
            return {"plan": None}
        return {
            "plan": {
                "disease": plan.get("disease"),
                "severity": plan.get("severity"),
                "created_at": plan.get("createdAt"),
                "plan_data": plan.get("planData", {}),
            }
        }

    async def _tool_generate_recovery_plan(self, user_id: str, args: dict) -> dict:
        from api.v1.recovery import (
            _build_prompt,
            _extract_json,
            _get_default_plan,
            _merge_plan_data,
            _prediction_context,
        )
        from repositories.prediction_repository import PredictionRepository
        from repositories.recovery_repository import RecoveryPlanRepository

        prediction_id = args.get("prediction_id")
        pred = None
        if prediction_id:
            pred = await PredictionRepository().find_by_id(prediction_id)
        if pred is None:
            pred = await PredictionRepository().find_latest_by_user(user_id)
        if pred is None:
            return {"error": "No prediction found. Run a symptom check first."}

        context = _prediction_context(pred)
        try:
            result = await self.llm.invoke(_build_prompt(context), "", json_mode=True)
            plan_data = _merge_plan_data(_extract_json(result), context)
        except Exception as e:
            _logger.warning("Agent recovery plan generation failed (%s); using fallback", e)
            plan_data = _get_default_plan(context)

        repo = RecoveryPlanRepository()
        plan = await repo.create(
            user_id,
            pred.id,
            pred.prediction,
            pred.confidence,
            pred.severity,
            pred.symptoms,
            plan_data,
        )

        try:
            from api.v1.recovery import _notify_recovery_plan_email
            await _notify_recovery_plan_email(user_id, pred.prediction)
        except Exception as e:
            _logger.warning("Recovery plan email skipped: %s", e)

        return {
            "plan_id": str(plan.get("_id")),
            "disease": pred.prediction,
            "what_it_means": plan_data.get("what_it_means"),
        }

    async def _tool_get_reminders(self, user_id: str, args: dict) -> dict:
        from repositories.reminder_repository import ReminderRepository
        reminders = await ReminderRepository().find_by_user(user_id, limit=5)
        return {
            "reminders": [
                {
                    "id": str(r.get("_id")),
                    "medicine_name": r.get("medicine_name"),
                    "dosage": r.get("dosage"),
                    "status": r.get("status"),
                    "start_time": r.get("start_time"),
                    "email_reminder": r.get("email_reminder", False),
                }
                for r in reminders
            ]
        }

    async def _tool_create_reminder(self, user_id: str, args: dict) -> dict:
        from repositories.reminder_repository import ReminderRepository
        from schemas.reminder_schema import ReminderCreate

        validated = ReminderCreate(**args)
        reminder = await ReminderRepository().create(user_id, validated.model_dump())
        return {
            "reminder_id": str(reminder.get("_id")),
            "medicine_name": reminder.get("medicine_name"),
            "dosage": reminder.get("dosage"),
            "start_time": reminder.get("start_time"),
            "email_reminder": reminder.get("email_reminder", False),
        }

    async def _tool_update_reminder(self, user_id: str, args: dict) -> dict:
        from repositories.reminder_repository import ReminderRepository
        from schemas.reminder_schema import ReminderUpdate

        reminder_id = args.get("reminder_id")
        if not reminder_id:
            raise ValueError("reminder_id is required")
        repo = ReminderRepository()
        existing = await repo.find_by_id(reminder_id)
        if not existing or existing.get("userId") != user_id:
            raise ValueError("Reminder not found")
        update_data = ReminderUpdate(**{k: v for k, v in args.items() if k != "reminder_id"}).model_dump()
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if not update_data:
            raise ValueError("No fields to update")
        updated = await repo.update(reminder_id, update_data)
        return {
            "reminder_id": reminder_id,
            "medicine_name": updated.get("medicine_name"),
            "status": updated.get("status"),
        }

    async def _tool_delete_reminder(self, user_id: str, args: dict) -> dict:
        from repositories.reminder_repository import ReminderRepository

        reminder_id = args.get("reminder_id")
        if not reminder_id:
            raise ValueError("reminder_id is required")
        repo = ReminderRepository()
        existing = await repo.find_by_id(reminder_id)
        if not existing or existing.get("userId") != user_id:
            raise ValueError("Reminder not found")
        await repo.delete(reminder_id)
        return {"deleted_reminder_id": reminder_id}

    async def _tool_get_predictions(self, user_id: str, args: dict) -> dict:
        from repositories.prediction_repository import PredictionRepository
        predictions = await PredictionRepository().find_by_user(user_id, limit=5)
        return {
            "predictions": [
                {
                    "id": p.get("id"),
                    "prediction": p.get("prediction"),
                    "confidence": p.get("confidence"),
                    "severity": p.get("severity"),
                    "timestamp": p.get("timestamp"),
                }
                for p in predictions
            ]
        }

    async def _tool_ask_medical(self, user_id: str, args: dict) -> dict:
        from services.rag_service import RAGService

        query = (args.get("query") or "").strip()
        if not query:
            raise ValueError("query is required")
        rag = RAGService()
        try:
            answer = await rag.answer_with_rag(query, self.llm)
        except Exception as e:
            _logger.warning("RAG ask failed: %s", e)
            answer = await self.llm.answer_medical_question(question=query)
        return {"query": query, "answer": answer}

    # ------------------------------------------------------------------
    # Planning / finalization
    # ------------------------------------------------------------------

    def _parse_plan(self, raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.removeprefix("json")
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object in agent plan")
        return json.loads(text[start : end + 1])

    async def _plan(self, user_id: str, message: str, context: str, history: str) -> dict:
        descriptions = _read_tools()
        prompt = AGENT_SYSTEM_PROMPT.format(
            descriptions=descriptions,
            context=context,
            history=history or "(no prior messages)",
            message=message,
        )
        raw = await self.llm.invoke(
            prompt, "", json_mode=True, temperature=0.4, max_tokens=700
        )
        plan = self._parse_plan(raw)
        tool = plan.get("tool")
        name = None
        args: dict = {}
        if isinstance(tool, dict):
            name = tool.get("name")
            args = tool.get("args") or {}
        if name and name not in TOOL_DESCRIPTIONS:
            _logger.warning("Agent requested unknown tool %s", name)
            name = None
            args = {}
        confirm_required = bool(plan.get("confirm_required", False))
        if name in WRITE_TOOLS:
            confirm_required = True
        return {
            "reply": plan.get("reply") or "How can I help?",
            "tool_name": name,
            "args": args,
            "action_summary": plan.get("action_summary") or "",
            "confirm_required": confirm_required,
        }

    async def _finalize(self, tool_summary: str, result: dict) -> str:
        try:
            prompt = FINALIZE_PROMPT.format(
                tool_summary=tool_summary,
                result=json.dumps(result, default=str, indent=2)[:1500],
            )
            reply = await self.llm.invoke(
                prompt, "", temperature=0.5, max_tokens=400
            )
            return reply.strip()
        except Exception as e:
            _logger.warning("Finalize failed: %s", e)
            return f"I've completed that for you. Here is what happened:\n\n{json.dumps(result, default=str, indent=2)}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run_turn(
        self,
        user_id: str,
        session_id: str,
        message: str,
        history: list[dict],
        session_prediction_context: dict | None = None,
    ) -> tuple[str, PendingActionResponse | None]:
        context = await self._build_context(user_id, session_prediction_context)
        history_txt = "\n".join(
            f"{m.get('role')}: {m.get('content')}" for m in history[-8:]
        )
        plan = await self._plan(user_id, message, context, history_txt)

        if not plan["tool_name"]:
            return plan["reply"], None

        if plan["confirm_required"]:
            from repositories.agent_repository import PendingActionRepository

            await PendingActionRepository().expire_stale(user_id)
            action = await PendingActionRepository().create(
                user_id, session_id, plan["tool_name"], plan["args"], plan["action_summary"]
            )
            pending = PendingActionResponse(
                id=str(action["_id"]),
                session_id=session_id,
                tool=plan["tool_name"],
                args=plan["args"],
                summary=plan["action_summary"] or plan["tool_name"],
                status=action["status"],
                created_at=action["createdAt"],
                expires_at=action["expiresAt"],
            )
            return plan["reply"], pending

        # Read-only tool — execute and finalize
        try:
            result = await self._execute_tool(user_id, plan["tool_name"], plan["args"])
        except Exception as e:
            _logger.warning("Read tool %s failed: %s", plan["tool_name"], e)
            return (
                (
                    f"I couldn't complete that right now ({e}). "
                    "Please try again or consult a healthcare professional."
                ),
                None,
            )
        tool_summary = f"{plan['tool_name']}({json.dumps(plan['args'], default=str)})"
        reply = await self._finalize(tool_summary, result)
        return reply, None

    async def confirm_action(
        self, user_id: str, pending_action_id: str, decision: str
    ) -> tuple[str, PendingActionResponse | None]:
        from repositories.agent_repository import PendingActionRepository

        repo = PendingActionRepository()
        action = await repo.find_by_id(pending_action_id)
        if not action:
            raise ValueError("Action not found")
        if action.get("userId") != user_id:
            raise ValueError("Action not found")
        if action.get("status") != "pending":
            raise ValueError("This action has already been handled")
        if action.get("expiresAt") and action.get("expiresAt") < datetime.now(UTC).isoformat():
            await repo.mark_resolved(pending_action_id, "expired")
            raise ValueError("This action has expired. Please ask again.")

        if decision == "decline":
            await repo.mark_resolved(pending_action_id, "declined")
            reply = (
                "No problem — I won't do that. Is there anything else I can help you with?"
            )
            return reply, None

        tool = action.get("tool")
        args = action.get("args") or {}
        try:
            result = await self._execute_tool(user_id, tool, args)
        except Exception as e:
            _logger.warning("Confirmed tool %s failed: %s", tool, e)
            await repo.mark_resolved(pending_action_id, "failed", error=str(e))
            return (
                f"I wasn't able to complete that: {e}. Please try again or ask for help.",
                None,
            )

        await repo.mark_resolved(pending_action_id, "approved", result=result)
        tool_summary = f"{tool}({json.dumps(args, default=str)})"
        reply = await self._finalize(tool_summary, result)
        return reply, None