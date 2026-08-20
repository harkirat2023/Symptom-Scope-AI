# SymptomScope AI — Implementation Results (Recovery Plan, Agent, Email, PDF)

> **Scope:** Fix the Recovery Plan failure, remove the Keyboard Shortcuts feature, upgrade the Health
> Assistant into a goal-driven Groq-only AI agent, make reminder/recovery emails functional, improve the
> PDF report (CSV untouched), preserve Clerk auth, and validate every user journey.

- Date: 2026-08-20
- Environment verified on: Windows, Python 3.14.4 (backend venv), Node/Next.js 15.4.10 (frontend),
  local MongoDB, Groq LLM (`openai/gpt-oss-120b`).

---

## 1. Recovery Plan — Root-Cause Fix

**Root cause of the "Failed to fetch" (500):** `backend/api/v1/recovery.py` called `pred.get(...)` on a
pydantic `PredictionRecord`, which has no `.get()` → `AttributeError` → 500 → the browser reported
"Failed to fetch".

**Fixes:**
- `backend/schemas/prediction_schema.py` — `PredictionRecord` now carries the enriched context:
  `age`, `gender`, `existing_conditions`, `symptom_duration`, `pain_level`.
- `backend/repositories/prediction_repository.py` — `create` / `find_by_id` / `find_by_user` /
  `find_latest_by_user` populate the new fields (DB keys `existingConditions` / `symptomDuration` /
  `painLevel`).
- `backend/schemas/recovery_schema.py` — added `what_it_means`, `what_to_do`,
  `personalized_recommendations` to `RecoveryPlanResponse`.
- `backend/api/v1/recovery.py` — rewritten: attribute access (root-cause fix), `_prediction_context()`,
  `_build_prompt()` (what-it-means, what-to-do, diet, exercise, sleep, warnings, doctor visit,
  personalized recs), robust `_extract_json()`, `_merge_plan_data()` (fills any missing LLM section
  from the structured fallback so the response always contains every field), `_get_default_plan()`
  (educational fallback — never fabricates), `_format_plan_response()`. Endpoints preserved:
  generate / latest / history / regenerate.
- `frontend/src/lib/api/recovery.ts` — new fields in the TS interface + error parsing that surfaces the
  backend `detail` instead of raw JSON text.
- `frontend/src/app/(dashboard)/recovery-plan/page.tsx` — renders "What This Condition Means",
  "What to Do Now", and "Personalized Recommendations" sections.

**LLM provider fix (was blocking ALL Groq generation):** the configured model
`llama-3.3-70b-versatile` returns HTTP 404 from the Groq API ("does not exist or you do not have access
to it"). The key was verified against `GET https://api.groq.com/openai/v1/models`; `openai/gpt-oss-120b`
was selected and set in both `backend/.env` (`GROQ_MODEL`) and `utils/settings.py` (`groq_model`
default). `LLMService.invoke` gained a `json_mode` flag that uses Groq JSON mode
(`response_format={"type":"json_object"}`) so structured output parses reliably. `GROQ_MAX_TOKENS` was
raised to 2048.

**Verified:** full generate flow returns 200 with every section populated (real prediction → Groq →
stored → fetched).

## 2. Keyboard Shortcuts — Removed

- Deleted `frontend/src/components/features/keyboard-shortcuts.tsx`.
- Rewrote `frontend/src/app/providers.tsx` without the dynamic import/render of the shortcuts widget.
- Repo-wide search for `keyboard|shortcut` (frontend, docs, config) returns nothing.

## 3. Goal-Driven Health Assistant Agent

New files / changes:
- `backend/services/agent_service.py` — the agent. Per turn it: builds context (profile, latest
  prediction, recovery plan, reminders, goal status) → asks Groq (JSON mode) for a plan
  (`{reply, tool, action_summary, confirm_required}`) → either replies, auto-runs a **read-only** tool,
  or (for **write** tools) creates a pending action and asks for confirmation. Write tools are
  hard-enforced: `confirm_required` is forced `true` for them regardless of the model output, and
  unknown tool names are dropped.
- Tools: `get_profile`, `update_profile` (email/location/health_goals), `get_recovery_plan`,
  `generate_recovery_plan`, `get_reminders`, `create_reminder`, `update_reminder`, `delete_reminder`,
  `get_predictions`, `ask_medical` (RAG).
- `backend/repositories/agent_repository.py` — `ProfileRepository` (upsert on `user_health_profiles`,
  the collection that already had a unique index) and `PendingActionRepository` (pending actions with
  24h TTL, status transitions, stale expiry).
- `backend/api/v1/chat.py` — `send_message` now runs the agent; new `POST /api/v1/chat/confirm`
  (`{pending_action_id, decision}`) executes/declines the stored action and returns the final reply.
- `backend/schemas/chat_schema.py` — `PendingActionResponse`; `ChatMessageResponse` gained optional
  `pending_action`; `ConfirmActionRequest`.
- `backend/utils/database.py` — indexes for `pending_actions`.
- Frontend: `chat.ts` (types + `confirmChatAction`), `chat-store.ts` (pending-action state),
  `chat-message.tsx` (inline Approve/Decline card), `chat-panel.tsx` (resolve flow), `empty-state.tsx`
  (goal-oriented example prompts).

**Safety:** all write operations require explicit user confirmation in the UI; the backend enforces it
even if the model disagrees. Clerk auth is untouched and still required for every chat/confirm request
(dev-mode fallback only in dev).

## 4. Email Functionality (config-gated)

- `backend/services/email_service.py` — rewritten: proper HMAC-signed one-click links
  (`reminder_id:action:user_id:expires`), `verify_action_signature()`, shared `_send()` helper,
  `send_reminder_email()` (fixed signature), new `send_recovery_plan_email()`. Links are built from
  `PUBLIC_BASE_URL` so they point at the backend action route (previously a non-existent Vercel path).
- `backend/services/reminder_service.py` — fixed the broken `send_reminder_email(...)` call (was
  missing `reminder_id` and `user_id` → TypeError). Recipient email is resolved from the health profile
  (captured by the agent) first, with the legacy `users` collection as fallback.
- `backend/api/v1/reminders.py` — new public `GET /api/v1/reminders/{id}/action` (signed, no auth)
  that verifies the signature/expiry, logs taken/missed, and returns an HTML confirmation page.
- `backend/api/v1/recovery.py` + `backend/services/agent_service.py` — `_notify_recovery_plan_email()`
  sends a "your plan is ready" email when a plan is generated and the user has a saved email.
- Config: `SMTP_HOST/PORT/USER/PASSWORD/FROM_EMAIL` and `PUBLIC_BASE_URL` added to `.env.example`
  (commented) and `backend/.env` (commented). When SMTP is unset, all sends are skipped gracefully and
  the rest of the app is unaffected. No credentials are hardcoded.

## 5. PDF Report Improvements

- `backend/services/report_export_service.py`
  - `generate_pdf` — history table cells are now wrapped `Paragraph` objects (no more clipped/overflow
    text), header styled, `VALIGN=MIDDLE`, alternating rows retained.
  - `generate_pdf_detailed` — new optional `recovery_plan` argument renders a "Recovery Plan Summary"
    section (condition, what-it-means, what-to-do, personalized recs) and each prediction now includes
    demographics, existing conditions, symptom duration, and pain level.
- `backend/api/v1/export.py` — the detailed PDF endpoint fetches and passes the latest recovery plan.
- **CSV export was not touched** (format and behavior unchanged).

## 6. Validation

### Backend
- `python -m py_compile` — all edited files OK.
- `pytest tests/` — new suites added: `test_recovery_plan.py`, `test_agent_service.py`,
  `test_email_service.py` (26 tests, all pass). Full suite: all pass **except three pre-existing
  failures unrelated to these changes**:
  1. `test_severity_service.py::test_classify_mild` — severity-classification assertion
     (`classify("Mild Food Poisoning")` → `Moderate`); severity code untouched.
  2. `test_predictions_api.py::test_predict_symptoms` — SHAP `TreeExplainer` additivity check
     failure (test mock model/feature mismatch); prediction/explainability paths untouched.
  3. `test_predictions_api.py::test_doctors_endpoint` — intermittent native crash on Windows /
     Python 3.14 ("Windows fatal exception: access violation"); same class of pre-existing native
     issue noted in `docs/PHASE3_P1_RESULTS.md`. CI (Python 3.11) is unaffected.

### Frontend
- `npm run lint` — 0 errors (1 pre-existing warning in generated `coverage/` output).
- `npx tsc --noEmit` — clean.
- `npm run test` — 135 tests passed (20 files).
- `npm run build` — succeeded.

### Runtime E2E (isolated test DB + dev-mode API)
Ran the real FastAPI app against `symptomscope_test` (isolated MongoDB DB + isolated Chroma path,
`DEV_MODE=true`, port 8099):
1. `POST /api/v1/predict` → 200, prediction stored.
2. `POST /api/v1/recovery-plan/generate` → 200 with all sections.
3. `GET /api/v1/recovery-plan/latest` → 200.
4. `POST /api/v1/chat/session` → 200.
5. `POST /api/v1/chat/message` (create reminder) → pending action returned, **not** executed.
6. `POST /api/v1/chat/confirm approve` → reminder created; reply summarizes it.
7. `GET /api/v1/reminders` → includes the new reminder.
8. Signed action link: tampered/expired signature → 400; valid link → 200 "Status logged".
9. `GET /api/v1/export/csv` → 200 CSV.
10. `GET /api/v1/export/pdf?detailed=true` → 200 `%PDF`.
The isolated test DB was dropped afterward; the production DB was verified free of test artifacts.

## 7. Configuration Notes

- `backend/.env` / `backend/.env.example`:
  - `GROQ_MODEL=openai/gpt-oss-120b` (validated against the Groq API for this key).
  - `PUBLIC_BASE_URL` — set to the deployed backend origin so email links resolve.
  - `SMTP_*` — set in production to enable reminder/recovery emails (all optional).
- `SECRET_KEY` should be a long random value in production — it signs the email action links.

## 8. Known Limitations

- Emails are fully wired and tested (signing, routing, scheduling, recipient resolution), but no
  external SMTP send was performed (no credentials available); all paths degrade gracefully.
- The agent requires Groq to be reachable; if it fails, the chat replies with a friendly error and the
  write tools are not executed.