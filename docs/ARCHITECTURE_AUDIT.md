# SymptomScope AI — Architecture Audit

> **Phase 1 — AUDIT ONLY.** This document describes the current architecture, a proposed target architecture,
> and a prioritized cleanup plan. **No code has been changed.** Every item below is a finding, not a fix.
> Anything rated below 90% confidence is flagged and must not be deleted without further verification.
> Any actual code changes (Phase 2) require explicit user approval.

- Date: 2026-08-15
- Repo: `harkirat2023/Symptom-Scope-AI`
- Branch: `main` (working tree clean at time of audit)

---

## 1. Current Architecture

### 1.1 Repository layout (monorepo)

```
Symptom Scope AI/
├── frontend/                 Next.js 15 (App Router), React 19, TypeScript
│   └── src/
│       ├── app/(dashboard)/  dashboard, history, recovery-plan, reminders,
│       │                     reports, results, settings, symptom-checker
│       ├── app/(auth)/       Clerk sign-in / sign-up
│       ├── components/       features/*, ui/* (Base UI wrappers), layouts/*, shared/*
│       ├── lib/api/          chat.ts, predictions.ts, recovery.ts, reminders.ts, risk-score.ts
│       ├── lib/stores/       chat, dashboard, reminder, risk-score, symptom, theme (Zustand)
│       ├── lib/validations/  symptom-form.ts (Zod)
│       └── middleware.ts      clerkMiddleware w/ try-catch fallback
├── backend/                  FastAPI + motor (MongoDB) + Redis
│   ├── api/v1/               predict, doctors, reports, symptoms, hospitals,
│   │                         analytics, export, chat, reminders, risk_score, recovery
│   ├── services/             LLM (Groq), prediction, analytics, risk-score, RAG, report,
│   │                         severity, emergency, precaution, doctor, hospital, ...
│   ├── repositories/         prediction, risk_score, chat, recovery, reminder, doctor, hospital
│   ├── schemas/              Pydantic v2 models
│   ├── auth/dependency.py    Clerk JWKS verification + dev_mode fallback
│   ├── utils/                settings.py, database.py, rate_limit.py
│   ├── ml/                   models/*.pkl, training/, preprocessing/, rag/, prompts/, data/
│   ├── bin/                  audit.py, startup_check.py
│   └── tests/                14 test modules (service + API, mocked DB)
├── .github/workflows/ci.yml  backend ruff/mypy/pytest; frontend lint/build
├── docker-compose.yml        mongodb:7.0 + redis:7.0
├── render.yaml               backend web service (uvicorn)
└── package.json              ROOT — misplaced @vitest/coverage-v8 devDep (bug, see §4 P0)
```

### 1.2 Backend stack & request flow

**Stack:** FastAPI ≥0.115, Pydantic v2, motor (MongoDB), slowapi + Redis (rate limiting),
scikit-learn (DecisionTree/RandomForest/NaiveBayes pickled models + TF-IDF embeddings),
LangChain + **Groq** (`openai/gpt-oss-120b`, validated against the Groq API) for chat/agent/explain/
follow-up/medical-QA and recovery-plan generation,
ChromaDB for RAG, reportlab (PDF export).

**Primary request flow (prediction):**

```
frontend symptom-checker
  → POST /api/v1/predict {symptoms, age, gender, existing_conditions, ...}
  → services/prediction_service.py
      feature_engineering + model_registry (pickled models)
      severity_service → precaution_service → emergency_service
      doctor_service / hospital_service (recommendations)
  → response persisted to MongoDB (predictions collection)
```

**Read-side flows:**

- `/api/v1/reports/{user_id}` → `report_service` aggregates prediction history (`fetchUserReports`)
- `/api/v1/analytics/{user_id}?range=` → `analytics_service` produces charts/insights (`fetchAnalytics`)
- `/chat/session` + `/chat/message` → `chat_service` + `LLMService` (`createChatSession`, `sendChatMessage`)
- `/export/csv|pdf` → `report_export_service` (report-export.tsx)
- `/risk-score/*` → `risk_score_service` (risk-score store/card)
- `/reminders/*` → `reminder_service` (reminder store/cards/form)
- `/recovery-plan/generate|latest` → LLM-based recovery plan (`generateRecoveryPlan`, `getLatestRecoveryPlan`)
- `/symptoms/search`, `/doctors`, `/hospitals` → used by prediction flow internally; public search endpoints exist

### 1.3 Authentication

- Frontend: Clerk (`@clerk/nextjs`), `clerkMiddleware` in `middleware.ts` wrapped in try/catch so missing Clerk config degrades to public pages.
- Backend: `auth/dependency.py` — HTTPBearer, JWKS fetch from `settings.clerk_jwks_url`/`clerk_issuer`, RS256 verification, 1h JWKS cache.
- `settings.dev_mode = True` default → falls back to `"dev-user-id"` when no credentials or JWKS missing.
- Rate limiting: `utils/rate_limit.py` — slowapi, keyed on JWT sub when present.

### 1.4 Deployment & infra

- `render.yaml`: single web service (backend, `uvicorn main:app`), Python 3.11. **No Redis / Mongo / Frontend service declared here.**
- `docker-compose.yml`: local `mongodb:7.0` (port 27017) + `redis:7.0` (6379) only.
- CI (`.github/workflows/ci.yml`): backend ruff → mypy (continue-on-error) → pytest w/ coverage; frontend eslint (continue-on-error) → `next build`.

### 1.5 Oversized files (maintainability risk)

| File | Lines |
|---|---|
| `frontend/src/app/(dashboard)/recovery-plan/page.tsx` | 708 |
| `backend/services/disease_registry.py` | 707 |
| `backend/services/analytics_service.py` | 527 |
| `backend/services/report_export_service.py` | 366 |
| `frontend/src/lib/api/predictions.ts` | 354 |

---

## 2. Proposed Target Architecture

No API/contract changes; only internal structure. Goals: one source of truth per concept, delete dead code, split oversized files.

### 2.1 Frontend

- **Shared API client** — introduce `lib/api/client.ts` exporting a single `authHeaders()` + `API_URL` resolver; delete the 5 duplicate copies (see §6.1).
- **Shared severity constants** — single `severityColors`/`severityBadgeColors`/`SEVERITY_ORDER` source consumed by all charts/badges (see §6.2).
- **Shared date/time utils** — one formatter replacing 7+ inline `toLocaleDateString` call sites (see §6.4).
- **Page decomposition** — extract the 708-line recovery-plan page into feature components under `components/features/recovery-plan/`; delete the duplicate `results/page.tsx` re-implementation of `PredictionResults` (see §6.5).
- **Store hygiene** — keep only store members that are consumed; remove dead setters/fields (see §4 P1).
- **Fix misplaced dep** — move `@vitest/coverage-v8` from root `package.json` into `frontend/package.json` so `npm run test:coverage` works (see §4 P0).

### 2.2 Backend

- **Consolidated constants** — single `RANGE_DAYS` in `utils/constants.py` (see §6.3).
- **Contract alignment** — align `ShapExplanation` and `RiskScoreAnalytics` between `schemas/` and frontend types (or wire/remove the unused fields) (see §4 P0).
- **Dead service removal** — delete `services/recovery_service.py` (zero importers; `api/v1/recovery.py` uses `LLMService` directly), `ml/preprocessing/preprocess.py` (unused; production uses `feature_engineering.py`), `bin/audit.py` + `bin/startup_check.py` (stale/obsolete), and dead methods in `chat_service.py`/`llm_service.py`/`email_service.py` (see §5).
- **Obsolete config** — remove unused settings fields (`llm_api_url/key/model`, `gemini_*`, `embedding_model`, `rag_score_threshold`) once LLM/RAG call sites are confirmed Groq/TF-IDF-only (see §4 P2, flagged risky).

### 2.3 Shared / CI

- `.env.example` must not contain real-looking Clerk secrets (see §4 P2, risky).
- Consider adding a `verify` script per package so CI and humans run the identical checks (see §7).

---

## 3. Prioritized Cleanup List

### P0 — Latent bugs / contract risks (fix first)

| # | Item | Where | Confidence | Why |
|---|---|---|---|---|
| 1 | `@vitest/coverage-v8` lives in **root** `package.json`, not `frontend/package.json` | `package.json`, `frontend/package.json` | High | `frontend/package.json` declares `test:coverage` with `coverage.provider: "v8"`, but the package providing it is not installed in the frontend → coverage run fails. Move dep to frontend. |
| 2 | Backend `ShapExplanation` vs frontend `ShapExplanation` contract mismatch | `schemas/prediction_schema.py` vs `frontend/lib/api/predictions.ts:23-27` | High | Backend emits `base_value: float` + `feature_values: list[TopContributingSymptom]`; frontend declares `shap_values?: number[]`, `base_value?`, `features?`. Also `shap_explanation` is never consumed anywhere in the frontend. Align or drop. |
| 3 | Backend `RiskScoreAnalytics` vs frontend `RiskScoreAnalytics` mismatch | `schemas/analytics_schema.py:91-94` vs `frontend/lib/api/predictions.ts:319-323` | High | Backend: `current_score/category/last_computed`. Frontend: `current_score/category/breakdown`. Grep for `last_computed` = 0 hits in frontend. `analytics.risk_score` is never read by dashboard components. Align or drop. |

### P1 — Dead code deletion (low risk, no behavior change)

| # | Item | Where | Confidence | Action |
|---|---|---|---|---|
| 4 | Stale backup files | `frontend/src/app/(dashboard)/results/page.tsx.bak`, `frontend/src/components/layouts/dashboard-sidebar.tsx.bak` | High | Delete `.bak` files (not wired into build). |
| 5 | Unused component | `frontend/src/components/features/history/health-summary-strip.tsx` | High (grep 0 refs) | Delete. |
| 6 | Unused re-export component | `frontend/src/components/shared/severity-badge.tsx` | High | 3-line re-export; consumers import `severityColors` from `dashboard-types.ts` directly. Delete. |
| 7 | Unused UI wrappers | `frontend/src/components/ui/dropdown-menu.tsx` (268 ln), `ui/sheet.tsx` (138 ln) | High | 0 importers across `src`. Delete (unless Base UI migration plans to use them). |
| 8 | Unused frontend API exports | `predictions.ts:173 fetchDoctors`, `predictions.ts:199 fetchSymptoms`, `chat.ts:53 getChatSessions`, `chat.ts:81 getChatMessages`, `recovery.ts getRecoveryPlanHistory` | High | 0 callers in app + tests. Delete exports. |
| 9 | Dead store members | `chat-store.ts` (`toggle`, `setMessages`, `setPredictionContext`, `reset`); `dashboard-store.ts` (`sidebarOpen`/`toggleSidebar`/`setSidebarOpen` — only tests use them, layout uses local `useState`); `risk-score-store.ts` (`setScore`, `setHistory`, `setTips`, `setProfile`) | High | Remove unused members; keep `setSelectedTimeRange` (used by dashboard/reports pages) and risk-store actions (`fetchScore` etc.). |
| 10 | Dead backend service file | `backend/services/recovery_service.py` (`RecoveryPlanService`, 229 ln) | High (0 importers) | Delete; `api/v1/recovery.py` uses `LLMService` directly. |
| 11 | Dead backend preprocess file | `backend/ml/preprocessing/preprocess.py` | High | Unused; production path is `services/feature_engineering.py`. Keep `ml/constants.py` (referenced). |
| 12 | CLI-only init script | `backend/ml/rag/init_knowledge_base.py` | Medium | CLI/manual only; no runtime importer. Verify knowledge base is pre-built before deleting. |
| 13 | Obsolete bin scripts | `backend/bin/audit.py` (refs dead endpoints `/analytics/summary`, `/risk-score` POST), `backend/bin/startup_check.py` (ref'd only in `DEPLOYMENT_FIX_REPORT.md:35`) | Medium | Candidate for deletion; confirm not used in deploy pipeline. |
| 14 | Root debug scripts (tracked, no refs) | `check_backend.py`, `simple_test.py`, `test_backend_recovery.py`, `test_backend_recovery2.py`, `test_frontend_api.js`, `test_recovery_endpoint.py`, `test_server.py` | High | Delete. |
| 15 | Dead backend methods | `chat_service.py`: `build_welcome_message` (:72), `explain_prediction` (:139), `generate_follow_up_questions` (:157), `answer_medical_question` (:171) — routes call `LLMService` directly; `llm_service.py:200 chat()` — 0 callers (deleting orphans `ml/prompts/chat.txt`); `email_service.py:85 process_reminder_action()` — never called; `explainability_service.py` `get_predicted_class_index`/`get_top_probability` — self-referenced only | High | Remove methods (keep the `LlmClient`/`process_message`/`build_system_prompt` path used by routes). |
| 16 | Unused imports / duplicate logging | `api/v1/recovery.py:8` unused `RecoveryPlanCreate`; `api/v1/chat.py:199-200` duplicate `import logging` + `_logger` block | High | Clean up. |
| 17 | Unused frontend dep | `nodemon` (devDep) | High | Not referenced by any script. Remove. |

### P2 — Dedup / refactor / extract

| # | Item | Where | Confidence | Action |
|---|---|---|---|---|
| 18 | `authHeaders()` × 5 copies | `lib/api/chat.ts:3`, `predictions.ts:127`, `recovery.ts:36`, `reminders.ts:3`, `risk-score.ts:52` | High | Extract to `lib/api/client.ts` (§2.1). |
| 19 | Severity color maps × 2 | `components/shared/dashboard-types.ts:13-23` vs `components/features/history/summary-charts.tsx:9-13` | High | Use one source (§2.1). |
| 20 | `RANGE_DAYS` × 3 | `repositories/prediction_repository.py:7`, `repositories/risk_score_repository.py:22`, `services/analytics_service.py:8` | High | Consolidate in `utils/constants.py`. |
| 21 | Date formatting ≥ 7 call sites | `toLocaleDateString` across frontend | Medium | Extract shared formatter. |
| 22 | `results/page.tsx` duplicates `PredictionResults` | `app/(dashboard)/results/page.tsx` (266 ln) | Medium | Reuse `components/features/prediction-results.tsx`; note file and `.bak` differ by one className. |
| 23 | Frontend test redefines module fns | `predictions.test.ts` redefines `fetchDoctors`/`fetchSymptoms` locally | Medium | Import from module. |
| 24 | Obsolete/dead config | `utils/settings.py`: `llm_api_url`, `llm_api_key`, `llm_model`, `gemini_*`, `embedding_model`, `rag_score_threshold` — 0 reads outside settings; frontend `.env.local` `NEXT_PUBLIC_POSTHOG_*`, `NEXT_PUBLIC_SENTRY_DSN` — 0 refs | Medium | Remove dead vars **only after** confirming no infra reads them (RAG/embeddings swap planned → keep `embedding_model` until then). |
| 25 | `disease_registry.py` (707 ln) / `analytics_service.py` (527 ln) / `report_export_service.py` (366 ln) | backend services | Low | Split into modules over time; no behavior change. |

---

## 4. Risky Areas / Do NOT Delete

- **Dependencies that look unused but are required:**
  - `cryptography` — used transitively by PyJWT RS256 / Clerk JWKS verification (`auth/dependency.py`). Do not remove.
  - `redis` — used by slowapi storage when `redis_url` set. Do not remove.
  - `@clerk/themes` — imported in `lib/clerk-provider.tsx`. Do not remove.
  - `@base-ui/react` — used by 10+ `components/ui/*` wrappers. Do not remove.
  - `langchain*` / `chromadb` — RAG + Groq chain. Do not remove.
- **LLM is Groq-only today.** `LLMService` docstring notes Gemini/OpenAI paths removed. Do not reintroduce; treat `gemini_*` settings as dead config (P2).
- **Endpoints with no frontend caller are still public API** — `chat/explain`, `chat/follow-up`, `chat/ask`, `chat/ask/basic`, `doctors/specialties`, `doctors/locations`, `symptoms/categories`, `symptoms`, `hospitals/locations`, `predictions/history`. Keep them; third parties or tests may rely on them.
- **`.env.example` contains real-looking Clerk test keys** (`pk_test_…`, `sk_test_…`). Test keys are low-value, but consider replacing with placeholders.
- **`dev_mode=True` default** — production should set `DEV_MODE=false` and real Clerk issuer/JWKS. Flag, not a code change.
- **Render config has no services beyond the backend** — Mongo/Redis/health checks are Docker/local only; verify production Mongo is provisioned elsewhere.
- Anything else not listed here as dead was found to have at least one live reference and is treated as used.

---

## 5. Safe-to-Delete (grep-verified, 0 importers)

```
frontend/src/app/(dashboard)/results/page.tsx.bak
frontend/src/components/layouts/dashboard-sidebar.tsx.bak
frontend/src/components/features/history/health-summary-strip.tsx
frontend/src/components/shared/severity-badge.tsx
frontend/src/components/ui/dropdown-menu.tsx
frontend/src/components/ui/sheet.tsx
backend/services/recovery_service.py
backend/ml/preprocessing/preprocess.py
backend/bin/audit.py            (verify no manual run)
backend/bin/startup_check.py    (only referenced by a .md)
check_backend.py
simple_test.py
test_backend_recovery.py
test_backend_recovery2.py
test_frontend_api.js
test_recovery_endpoint.py
test_server.py
```

---

## 6. Files to Merge / Move

1. **`authHeaders`** → single `lib/api/client.ts` (merge from 5 files).
2. **`severityColors`/`severityBadgeColors`/`SEVERITY_ORDER`** → keep `dashboard-types.ts` as the single source; update `summary-charts.tsx` and `report-charts.tsx`/`disease-charts-row.tsx`/`trend-charts-row.tsx` to import it.
3. **`RANGE_DAYS`** → `backend/utils/constants.py`; import from 3 repositories/services.
4. **Recovery-plan page** (708 ln) → extract step/tab components into `components/features/recovery-plan/`.
5. **`results/page.tsx`** → delegate to `PredictionResults`; delete `.bak`.
6. **`@vitest/coverage-v8`** → move from root to `frontend/package.json`.
7. **`symptom-form.ts`** — no move needed; leave as is (already single source for the symptom checker form).

---

## 7. Verification Commands

Run these before and after any Phase-2 change; the audit itself made **no** changes.

```bash
# Backend
cd backend
python -m pytest -q                                  # unit + API tests (mocked DB)
ruff check . --output-format=github                   # lint
mypy . --ignore-missing-imports                       # type check (CI allows failure)

# Frontend
cd frontend
npm run lint                                          # eslint
npm run test                                          # vitest run
npm run build                                         # next build (also needs @vitest/coverage-v8 fix for test:coverage)

# Smoke
docker compose up -d                                  # local Mongo + Redis
cd backend && uvicorn main:app --port 8080            # backend
cd frontend && npm run dev                            # frontend
```

> Note: `npm run test:coverage` currently fails at the frontend due to the misplaced `@vitest/coverage-v8` (P0 #1).

---

## 8. Confidence Notes

- All items in §5 and P1 are grep-verified as unreferenced (0 importers / 0 callers) at audit time.
- Items flagged *Medium* (12, 13, 21, 22, 23, 24) involve convention/documentation checks or possible external consumers — re-verify immediately before deleting.
- No claim of correctness beyond "audit-only"; nothing was fixed.
