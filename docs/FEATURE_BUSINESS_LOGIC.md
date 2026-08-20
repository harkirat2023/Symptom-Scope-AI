# SymptomScope AI — Feature Business Logic

This document describes **how every feature actually behaves in the codebase** — the business rules, execution order, data written, and cross-feature dependencies — as an architect-level reference. It is derived from static inspection of the source; it does not claim runtime results.

- **Backend**: FastAPI (`backend/`), MongoDB, Clerk JWT auth, Groq LLM (only provider), ChromaDB + TF-IDF RAG.
- **Frontend**: Next.js App Router (`frontend/`), Clerk middleware, React Markdown chat rendering.

---

## Table of Contents

1. [Authentication & Authorization](#1-authentication--authorization)
2. [Symptom Check / Prediction](#2-symptom-check--prediction)
3. [Risk Score](#3-risk-score)
4. [Prediction History](#4-prediction-history)
5. [Recovery Plan](#5-recovery-plan)
6. [Medication Reminders & Email (Yes/No)](#6-medication-reminders--email-yesno)
7. [AI Health Chat Agent](#7-ai-health-chat-agent)
8. [RAG Medical Knowledge QA](#8-rag-medical-knowledge-qa)
9. [Doctors & Hospitals](#9-doctors--hospitals)
10. [Emergency Detection](#10-emergency-detection)
11. [SHAP Explainability](#11-shap-explainability)
12. [Reports Export (CSV / PDF)](#12-reports-export-csv--pdf)
13. [Analytics](#13-analytics)
14. [AI Agent Tool Matrix](#14-ai-agent-tool-matrix)
15. [API ↔ Business Logic Matrix](#15-api--business-logic-matrix)
16. [Data Store ↔ Business Logic Matrix](#16-data-store--business-logic-matrix)
17. [Email Notification Matrix](#17-email-notification-matrix)
18. [Master End-to-End Workflows](#18-master-end-to-end-workflows)
19. [Cross-Cutting Dependencies](#19-cross-cutting-dependencies)
20. [Known Limitations & Ambiguities](#20-known-limitations--ambiguities)

---

## 1. Authentication & Authorization

**Owners**: `backend/auth/dependency.py`, `frontend/src/middleware.ts`, `backend/utils/settings.py`.

- The backend trusts **Clerk JWTs** (`RS256`). On each request `get_current_user`:
  1. If no `Authorization: Bearer` header and `dev_mode` is `true` → returns `"dev-user-id"` (dev fallback).
  2. If a token exists, fetches Clerk JWKS (cached 3600s), matches the token `kid`, decodes/verifies `exp` + issuer, and returns `payload["sub"]` as `user_id`.
- Every `/api/v1` endpoint (except the public signed reminder-action link) requires `Depends(get_current_user)`.
- **Data isolation** is enforced per-endpoint: prediction/recovery/reminder/chat/analytics reads and writes are scoped to `user_id`, and cross-user access returns `403`.
- `/analytics/{user_id}` additionally checks the path `user_id == auth_user_id`.
- **Frontend route protection** (`frontend/src/middleware.ts`, Clerk `createRouteMatcher`): protected paths are `/dashboard`, `/history`, `/reports`, `/settings`, `/symptom-checker`, `/results`, `/recovery-plan`, `/reminders`. A try/catch around Clerk middleware makes protection a no-op when Clerk config is missing (server-side guards still apply on the backend).
- **Security note**: `settings.dev_mode` defaults to `True`. In production this must be `False` with `CLERK_JWKS_URL` / `CLERK_ISSUER` set, otherwise unauthenticated requests are accepted as `dev-user-id`.

---

## 2. Symptom Check / Prediction

**Owner**: `backend/api/v1/predict.py` (`POST /predict`, 10/min), services in `backend/services/`.

Pipeline (in order):

1. **Validate** `SymptomInput` (symptoms 1–50; age 0–150; gender male|female|other; pain 0–10).
2. `FeatureEngineeringService.encode_symptoms` → feature vector.
3. `PredictionService.predict` → primary prediction + confidence + alternatives (24 alternatives for Kaggle model) + top contributing symptoms.
4. `SeverityService.classify(disease, confidence)` → `Mild | Moderate | Severe`.
5. `PrecautionService.get_precautions(disease, severity)` → curated precautions (from disease registry / DB).
6. `EmergencyService.detect(disease, confidence, severity)` → emergency flag + reasons + trigger breakdown (severity/confidence/escalation).
7. `DoctorService.get_specialty_for_disease` → recommended specialist (disease registry lookup).
8. `DoctorService.get_recommendations(disease, limit=3)` → up to 3 recommended doctors.
9. `ExplainabilityService.build_contributing_symptoms` → SHAP-based `base_value` + top contributing symptoms (see §11).
10. **Persist** `PredictionRecord` (userId, symptoms, prediction, confidence, severity, age, gender, existingConditions, symptomDuration, painLevel, timestamp=UTC ISO).
11. Invalidate the user's analytics cache.
12. **Risk score** is recomputed from the user's prediction history and persisted (`compute_and_save`), wrapped in try/except so a risk-score failure never fails the prediction (returns `None`).

Response: `PredictionResponse` — primary_prediction, confidence, alternatives, severity, top_contributing_symptoms, precautions, emergency, prediction_id, recommended_specialist, doctor_recommendations, explanation_summary, confidence_info, shap_explanation, risk_score, risk_category.

**Business rules**
- A prediction always persists and always returns a full enriched payload.
- Confidence is `0–100`.
- Doctors are computed live from the MongoDB-backed doctor repository at prediction time.

---

## 3. Risk Score

**Owners**: `backend/services/risk_score_service.py`, `backend/api/v1/risk_score.py`.

- Computed automatically after each prediction and saved to the `risk_scores` collection (score 0–100, category, breakdown, `predictionId`, timestamp).
- `/risk-score` returns the latest score + factor breakdown; `404` if none (message: run Symptom Checker first).
- `/risk-score/history?range=1m|3m|6m|1y` returns the score trend.
- `/risk-score/tips` returns guidance tips (from `get_tips`).
- `/risk-score/profile` (GET/PUT) manages an extended health profile (BMI, exercise frequency, diet type, smoking status, sleep hours, existing conditions) used as additional risk factors.
- Breakdown factors are validated through `RiskFactorBreakdown`; missing/extra keys are handled by the Pydantic schema.

---

## 4. Prediction History

**Owner**: `backend/api/v1/predict.py` (`GET /predictions/history`, `GET /predictions/latest`, 10/min).

- `find_by_user(user_id, limit)` returns up to 100 records (newest first by `timestamp`).
- Each history item returns `id`, `user_id`, `symptoms`, `prediction`, `confidence`, `severity`, `timestamp` (UTC ISO string) plus optional demographic fields.
- `GET /predictions/latest` returns a compact dict: `primary_prediction`, `confidence`, `severity`, `prediction_id`; `404` when empty. Used by the Recovery Plan flow and results page.

---

## 5. Recovery Plan

**Owner**: `backend/api/v1/recovery.py`, `backend/repositories/recovery_repository.py`.

Endpoints (all 10/min except generate 5/min, regenerate 3/min):

- `POST /recovery-plan/generate` — body `{prediction_id}`.
  - Validates the ID is a valid ObjectId and that the prediction belongs to the user (403 otherwise).
  - Builds patient context from the prediction.
  - **RAG grounding**: retrieves reference material for the disease from the RAG knowledge base (`_retrieve_reference_material`, best-effort; empty string if unavailable) and appends it to the prompt as reference-only material.
  - Calls Groq with `json_mode=True`; robustly extracts JSON (`_extract_json` handles code fences / stray prose).
  - Merges the LLM output over a **structured fallback plan** (`_merge_plan_data` + `_get_default_plan`) so every section always exists even if the LLM omits fields or fails.
  - Persists the plan; sends a config-gated "plan ready" email (`_notify_recovery_plan_email`), skipped if SMTP unconfigured or no profile email.
- `GET /recovery-plan/latest` — latest plan or 404.
- `GET /recovery-plan/history` — all plans for the user.
- `POST /recovery-plan/regenerate` — body `{plan_id}`; regenerates a new plan for the original prediction (with RAG grounding), updates in place (version bumps on the repo side).

**Plan JSON contract** (`_format_plan_response`): id, user_id, prediction_id, disease, confidence, severity, symptoms, what_it_means, what_to_do, recovery_timeline, diet_recommendations, foods_to_eat, foods_to_avoid, hydration_advice, sleep_recommendation, exercise_recommendation, daily_physical_activity, lifestyle_changes, personalized_recommendations, medicines_disclaimer, when_to_visit_doctor, emergency_warning_signs, mental_wellness_tips, recovery_checklist, progress_tracker, created_at, updated_at, version.

**Business rules**
- Never fabricates medications, dosages, credentials, hospital names, or emergency numbers (explicit prompt rules + conservative fallback).
- The plan is educational; disclaimers are mandatory.

---

## 6. Medication Reminders & Email (Yes/No)

**Owners**: `backend/api/v1/reminders.py`, `backend/services/reminder_service.py`, `backend/services/email_service.py`, `backend/repositories/reminder_repository.py`.

CRUD endpoints (10/min): `POST /reminders`, `GET /reminders?status=`, `PUT /reminders/{id}`, `DELETE /reminders/{id}`, `POST /reminders/{id}/log`, `GET /reminders/upcoming`.

Reminder fields: medicine_name, dosage, frequency (`daily` | `specific_days`), schedule_details, duration_days, start_time (HH:MM), status (`active|paused|completed`), `email_reminder` boolean, optional `linked_prediction_id`, `nextDueAt`.

**Email-at-time flow** (satisfies "option to give reminder in emails at that time"):
- `ReminderScheduler` polls every **300 s** (`_poll_loop`), finds due reminders (`find_due_reminders`), and when `email_reminder` is true:
  - Resolves the recipient email from the agent-captured health profile (`user_health_profiles`) or the legacy `users` collection.
  - Sends `send_reminder_email` — an HTML/plain email containing **YES (Mark as Taken)** and **NO (Mark as Missed)** buttons.
  - Updates `nextDueAt` for the next occurrence.
- Links are **HMAC-signed** (`_create_signed_action_link`): payload `reminder_id:action:user_id:expires`, `expires` = now + 48 h, HMAC-SHA256 with `secret_key`. The public handler `GET /reminders/{id}/action?action=taken|missed&user=...&expires=...&sig=...` verifies the signature + expiry before logging the status (`log_status`, note "Via email link") and returns a confirmation HTML page.
- Emails are **config-gated**: `EmailService.configured()` requires `smtp_host/user/password/from_email`; otherwise send is skipped with a warning (no crash).

**Business rules**
- Only `taken` / `missed` actions are accepted; invalid/expired signatures get a 400 page.
- The action endpoint is public-by-design (no auth) but cryptographically signed.
- `nextDueAt` is computed from `start_time` daily pattern.

---

## 7. AI Health Chat Agent

**Owners**: `backend/api/v1/chat.py`, `backend/services/agent_service.py`, `backend/repositories/chat_repository.py`.

Endpoints (rate limits): `POST /chat/session` (10/min), `GET /chat/sessions` (10/min), `POST /chat/message` (5/min), `POST /chat/confirm` (5/min), `GET /chat/messages/{session_id}` (10/min), `POST /chat/explain`, `/chat/follow-up`, `/chat/ask`, `/chat/ask/basic` (10/min).

**Agent turn logic** (`run_turn`):
1. Build context: user profile, latest prediction, recovery plan, reminders (5), session prediction context, and computed **goal status** (collect email+location → run symptom check → generate recovery plan → set up reminders).
2. Plan: the LLM (Groq, `json_mode=True`, temp 0.4) returns `{reply, tool, action_summary, confirm_required}`. Unknown tool names are dropped; any tool in `WRITE_TOOLS` forces `confirm_required=true`.
3. **Write tools** → a `PendingAction` is created (24 h TTL), returned to the frontend, and the UI renders an Approve/Decline card. The write runs **only** after `POST /chat/confirm`.
4. **Read tools** → executed immediately and summarized by `_finalize`.

**Write protection**: `WRITE_TOOLS = {update_profile, generate_recovery_plan, create_reminder, update_reminder, delete_reminder}`. Server-enforced (not merely a prompt hint) — `_plan` forces `confirm_required` and `confirm_action` is the only path that executes stored writes.

**Structured output**: assistant replies are formatted as **Markdown** (short lead-in, bullet/numbered lists, next-step line) per the system/finalize prompts, and the frontend renders them with `react-markdown` + `remark-gfm` (`chat-message.tsx`).

**Session handling**: `POST /chat/session` may accept a `prediction_id` to seed `predictionContext` (disease/confidence/severity/symptoms); stale sessions are deactivated; sending to an inactive session → 400; message validation enforced.

---

## 8. RAG Medical Knowledge QA

**Owner**: `backend/services/rag_service.py`, `POST /chat/ask`, `POST /chat/ask/basic`.

- Knowledge base: `backend/ml/rag/knowledge/*.txt|*.md` → chunked (500/50) → embedded with a **TF-IDF adapter** (scikit-learn; no torch/Gemini embeddings) → stored in ChromaDB (`./ml/rag/chromadb`, collection `medical_knowledge`).
- `answer_with_rag(question, llm)`: if the KB has documents, retrieves top-k context and passes `[Source: ...]` + content to the LLM; otherwise falls back to plain LLM medical QA.
- `/chat/ask` reports `rag_source` = whether the KB had documents. If `GROQ_API_KEY` is unset, returns a friendly "not configured" message.
- `initialize_knowledge_base()` rebuilds the store if the collection was created by a different embedding adapter (dimension mismatch protection).
- RAG is also used for **recovery-plan grounding** (§5) and by the agent `ask_medical` tool.

---

## 9. Doctors & Hospitals

**Owners**: `backend/services/doctor_service.py`, `backend/services/hospital_service.py`, repositories + `backend/services/disease_registry.py`.

- Doctors: `DoctorService.get_recommendations(disease|specialty|location|query|sort, limit)` — MongoDB-backed; scores by specialty relevance (disease → `get_specialist` mapping), location relevance, rating, query; sortable by rating/distance/availability; serialized output (name, specialty, location, rating, distance_km, availability, phone, hospital, experience_years).
- Hospitals: `HospitalService.search(query|location|specialty|disease|emergency_only|sort, limit)` — scores by department match (specialty → department map), location, emergency capability, rating; serialized (name, location, specialties, rating, distance_km, phone, emergency, has_ambulance, bed_count, address).
- Disease → specialist mapping lives in the **disease registry** (`services/disease_registry.py`) and drives both prediction-time doctor recommendations and these services.
- Exposed via `/doctors` and `/hospitals` endpoints (verified live) and now via the agent's `get_doctors` / `get_hospitals` read tools.

---

## 10. Emergency Detection

**Owner**: `backend/services/emergency_service.py` (called from `predict.py`).

- Inputs: disease, confidence, severity.
- Produces `is_emergency`, `reasons`, and the trigger breakdown (`severity_triggered`, `confidence_triggered`, `escalation_triggered`).
- Drives the results page's emergency banner and prompts the user to seek immediate care / hospitals.

---

## 11. SHAP Explainability

**Owner**: `backend/services/explainability_service.py` (called from `predict.py`).

- `build_contributing_symptoms(encoded_features, class_idx, top_probability)` returns `base_value` + top contributing symptoms with `symptom`, `importance`, `shap_value`, `relative_contribution_pct`.
- Rendered on the results page as "why this prediction" and used in `explanation_summary`.
- This was the prior fix that made live `/predict` return full SHAP data (model path in sync with the service).

---

## 12. Reports Export (CSV / PDF)

**Owner**: `backend/services/report_export_service.py` + report endpoints (verified live: CSV and PDF exports return correct content types; PDFs carry the `%PDF` magic).

- `generate_csv`: header + one row per prediction (Timestamp, Symptoms, Predicted Disease, Confidence, Severity, Specialist, Precautions).
- `generate_csv_summary`: metadata header (generated-at, totals, risk score), severity distribution, most-common condition, full history block.
- `generate_pdf` (reportlab): branded title, executive-summary table (total, unique conditions, most common, avg confidence, severe/moderate/mild, risk score), prediction-history table (Date/Symptoms/Prediction/Confidence/Severity), disclaimer footer.
- `generate_pdf_detailed`: recovery-plan summary section (condition/confidence/severity, what-it-means, what-to-do, personalized recommendations) + per-check-up detail blocks (demographics, existing conditions, duration, pain level, specialist, precautions).
- All exports are educational and carry a medical disclaimer.

---

## 13. Analytics

**Owner**: `backend/api/v1/analytics.py`, `backend/services/analytics_service.py`.

- `GET /analytics/{user_id}?range=1m|3m|6m|1y` — returns aggregated trends (risk trend, severity distribution, etc.) over the requested window; guarded by path-owner check.
- Responses are cached in-memory (`_ANALYTICS_CACHE`, TTL) and **invalidated on each new prediction** (predict.py calls `invalidate_user_cache`).
- Includes the latest persisted risk score (from `risk_scores`).

---

## 14. AI Agent Tool Matrix

| Tool | Type | Effect | Runs when |
|---|---|---|---|
| `get_profile` | read | Return email/location/health goals | auto |
| `update_profile` | write | Upsert email/location/health goals | on Approve |
| `get_recovery_plan` | read | Latest plan summary | auto |
| `generate_recovery_plan` | write | Generate + persist plan (RAG-grounded) | on Approve |
| `get_reminders` | read | List reminders (5) | auto |
| `create_reminder` | write | Create reminder | on Approve |
| `update_reminder` | write | Update reminder | on Approve |
| `delete_reminder` | write | Delete reminder | on Approve |
| `get_predictions` | read | Prediction history (5) | auto |
| `get_doctors` | read | Recommended doctors (disease/location) | auto |
| `get_hospitals` | read | Nearby hospitals (disease/location/emergency) | auto |
| `ask_medical` | read | RAG medical answer | auto |

---

## 15. API ↔ Business Logic Matrix

| Endpoint | Rate | Core business logic |
|---|---|---|
| `POST /predict` | 10/min | Full prediction pipeline (§2) + risk score |
| `GET /predictions/history` | 10/min | History with timestamps (§4) |
| `GET /predictions/latest` | 10/min | Compact latest (§4) |
| `GET /risk-score`, `/history`, `/tips`, `/profile` | 10/min | Risk score read/tips/profile (§3) |
| `PUT /risk-score/profile` | 10/min | Health-profile upsert |
| `POST /recovery-plan/generate` | 5/min | LLM + RAG + fallback merge, persist, email (§5) |
| `GET /recovery-plan/latest`, `/history` | 10/min | Plan reads |
| `POST /recovery-plan/regenerate` | 3/min | Fresh plan, same prediction |
| `POST|GET /reminders`, `PUT|DELETE /reminders/{id}`, `POST .../log`, `GET .../upcoming` | 10/min | Reminder CRUD/log/upcoming (§6) |
| `GET /reminders/{id}/action` | public | Signed Yes/No email link (§6) |
| `POST /chat/session`, `GET /chat/sessions`, `POST /chat/message`, `POST /chat/confirm`, `GET /chat/messages/{id}` | 10/10/5/5/10 | Agent turn + write confirmation (§7) |
| `POST /chat/explain`, `/follow-up`, `/ask`, `/ask/basic` | 10/min | LLM explanation / follow-ups / RAG QA (§8) |
| `GET /analytics/{user_id}` | 10/min | Aggregated analytics + cached risk score (§13) |
| Reports (CSV/PDF) | — | Report export service (§12) |

---

## 16. Data Store ↔ Business Logic Matrix

| Collection | Written by | Read by |
|---|---|---|
| `predictions` | predict | history, latest, analytics, risk recompute, recovery (context), agent context |
| `recovery_plans` | generate/regenerate (+agent) | latest, history, agent context |
| `reminders` | reminder CRUD (+agent) | list/upcoming, scheduler, agent context |
| `reminder_logs` | action link, `/log` | (status tracking) |
| `risk_scores` | risk-score service (per prediction) | `/risk-score`, analytics |
| `user_health_profiles` | agent `update_profile`, profile endpoint | scheduler email resolution, agent context |
| `pending_actions` | agent (24 h TTL) | confirm flow |
| `chat_sessions` / `chat_messages` | chat endpoints | session list / history |
| `doctors` / `hospitals` | seed data (Mongo) | predict-time recommendations, search services, agent tools |
| ChromaDB `medical_knowledge` | RAG init | `/chat/ask`, agent `ask_medical`, recovery grounding |

---

## 17. Email Notification Matrix

| Email | Trigger | Gating | Actions |
|---|---|---|---|
| Reminder (medicine, dosage) | Scheduler every 300 s for due reminders with `email_reminder=true` | SMTP configured + recipient email resolved | YES=taken / NO=missed (HMAC-signed, 48 h) |
| Recovery plan ready | After plan generate/regenerate (or agent) | SMTP configured + profile email present | none (link to app) |

---

## 18. Master End-to-End Workflows

**A. New user → recovery plan**
1. Sign in via Clerk; middleware protects dashboard routes.
2. Symptom Checker → `POST /predict` → full result + risk score.
3. Results page shows SHAP + precautions + emergency + doctors.
4. Recovery Plan page → `POST /recovery-plan/generate` (RAG-grounded) → plan saved + notification email (if configured).
5. Agent can generate the same plan via `generate_recovery_plan` (approval required).

**B. Reminder with email**
1. User (or agent) creates a reminder with `email_reminder=true` and saves profile email.
2. Scheduler sends the email at the reminder time with YES/NO links.
3. User clicks a link → signed verification → status logged.

**C. Agent conversation**
1. User opens the chat; session created (optionally seeded with a prediction).
2. User message → plan (write → pending card; read → instant).
3. User approves → write executed → structured Markdown summary.

**D. Reporting**
1. History page lists predictions (timestamps).
2. Reports page exports CSV/PDF (standard or detailed with recovery plan).

---

## 19. Cross-Cutting Dependencies

- **Auth** feeds every API call; `dev_mode` must be `False` in production.
- **Predict** drives: risk score, history, recovery, analytics, agent context, doctors.
- **Profile email** is the single source for reminder/recovery emails (legacy `users.email` fallback).
- **RAG KB** (Chroma + TF-IDF) powers medical QA, the agent's `ask_medical`, and recovery grounding.
- **Groq** (`openai/gpt-oss-120b`) is the only LLM; rate-limited per endpoint; fail-soft design (fallbacks in prediction risk score, recovery plans, RAG, agent read errors).
- **Rate limiter** applied per endpoint via `utils.rate_limit`.

---

## 20. Known Limitations & Ambiguities

- **ML provenance**: training code (`kaggle_pipeline.py`) targets the Kaggle 24-disease set (+5), while on-disk models were trained on a synthetic dataset (30 classes incl. Influenza). The code path (primary) uses the Kaggle-trained pipeline; the on-disk artifacts are a documented fallback. No retraining is performed at runtime.
- **Security hardening**: `dev_mode=True` default. Flip to `False` + set Clerk env vars for a truly protected production. (Not changed automatically because doing so without runtime verification could break live auth.)
- **Recovery plan & RAG**: grounding is best-effort and additive; if the KB is empty or Chroma is unavailable, generation proceeds unchanged (documented behavior, not an error).
- **Email delivery** depends on SMTP config; scheduler cadence is 300 s, so "at that time" is accurate to within that poll window.
- **Report exports** require `reportlab` (PDF) installed.
- **Ambiguity**: "AI agent must return the answer in well structured format" is implemented at the prompt + Markdown-rendering layer; the exact structure (headings vs bullets) is LLM-chosen rather than enforced by a fixed schema.