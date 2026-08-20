# SymptomScope AI — Phase 3: P1 Safe Cleanup Results

> **Phase 3 — P1 dead-code deletion (HIGH-confidence only).** Implements the high-confidence P1 items from
> `docs/ARCHITECTURE_AUDIT.md` §4 P1. Only items verified to have zero live references (repo-wide search of
> imports, package scripts, CI, Docker, Render, deployment config, and docs) were deleted. Anything with
> residual uncertainty was **skipped and reported** below rather than deleted.

- Date: 2026-08-15
- Prior phases: Phase 1 (audit, `docs/ARCHITECTURE_AUDIT.md`) and Phase 2 (P0 contract fixes) completed.
  `docs/PHASE2_P0_RESULTS.md` was not written in Phase 2; findings from Phase 2 are summarized at the end.

---

## 1. Deleted Files

### Frontend components (`frontend/src/`)
- `components/features/history/health-summary-strip.tsx` — self-references only (P1 #1).
- `components/shared/severity-badge.tsx` — no references anywhere (P1 #3).
- `components/ui/dropdown-menu.tsx` — no external imports (P1 #4).
- `components/ui/sheet.tsx` — no external imports (P1 #4).
- `app/(dashboard)/results/page.tsx.bak` — backup artifact, no references.
- `components/layouts/dashboard-sidebar.tsx.bak` — backup artifact, no references. (The live
  `dashboard-sidebar.tsx` differs from the `.bak` and is retained.)

### Backend (`backend/`)
- `services/recovery_service.py` — `RecoveryPlanService` had 0 importers; `api/v1/recovery.py` uses
  `LLMService` directly (P1 #10).
- `ml/preprocessing/preprocess.py` — unused; production path is `services/feature_engineering.py`
  (P1 #11). `ml/constants.py` retained (referenced).

### Root debug scripts (7 files)
- `check_backend.py`, `simple_test.py`, `test_backend_recovery.py`, `test_backend_recovery2.py`,
  `test_frontend_api.js`, `test_recovery_endpoint.py`, `test_server.py`
  — ad-hoc debug scripts with no references in code, CI, Docker, Render, deployment config, or docs.

---

## 2. Deleted Frontend API Exports

- `frontend/src/lib/api/predictions.ts`
  - `fetchDoctors()` — no external callers (`predictions.test.ts` defines and tests its **own local**
    `fetchDoctors`, so the module export was unused).
  - `fetchSymptoms()` — same pattern; no external callers.
  - Orphaned types `DoctorSearchResponse`, `SymptomResult`, `SymptomSearchResponse` (used only by the
    deleted functions).
- `frontend/src/lib/api/chat.ts`
  - `getChatSessions()` — no external callers.
  - `getChatMessages()` — no external callers.
  - Orphaned type `ChatSessionList` (used only by the deleted function).
- `frontend/src/lib/api/recovery.ts`
  - `getRecoveryPlanHistory()` — no external callers.
  - Orphaned type `RecoveryPlanListResponse` (used only by the deleted function).

---

## 3. Cleaned Zustand Store Members

- `frontend/src/lib/stores/chat-store.ts` — removed `toggle`, `setMessages`, `setPredictionContext`,
  `reset` (no external refs). Kept `clearChat` (used by `chat-panel.tsx:46,133,147`), the live state
  fields, and the used setters (`setOpen`, `setSession`, `addMessage`, `setLoading`, `setSending`,
  `setError`). The `predictionContext` state field is still read by `chat-panel.tsx` and was retained.
- `frontend/src/lib/stores/risk-score-store.ts` — removed `setScore`, `setHistory`, `setTips`,
  `setProfile` (no external refs). Kept `setGetToken` (used by `health-profile-form.tsx:213-217` and
  `risk-score-dashboard-card.tsx:22-27`), `setLoading`, `setError`, and the fetch actions.
- `frontend/src/lib/stores/dashboard-store.ts` — removed `sidebarOpen`, `toggleSidebar`,
  `setSidebarOpen` (production layout uses local `useState`; only the test used them). Kept
  `selectedTimeRange` / `setSelectedTimeRange` (used by dashboard/reports pages).
- `frontend/src/lib/stores/__tests__/dashboard-store.test.ts` — rewritten to test the retained members
  (`selectedTimeRange`, `setSelectedTimeRange`) instead of the removed sidebar members.

---

## 4. Deleted Backend Service Methods

- `backend/services/chat_service.py` — removed `build_welcome_message`, `explain_prediction`,
  `generate_follow_up_questions`, `answer_medical_question` (routes call `LLMService` directly) and the
  now-unused `self._llm` attribute. Kept the `LlmClient` / `build_system_prompt` / `process_message` /
  `validate_message` / `build_context` path used by routes (P1 #15).
- `backend/services/llm_service.py` — removed `chat()` (0 callers; P1 #15) and the orphaned
  `_default_chat_prompt()`. `ml/prompts/chat.txt` was **kept** because `backend/bin/startup_check.py:87`
  still references it.
- `backend/services/email_service.py` — removed `process_reminder_action()` (never called) and the
  unused `from fastapi import Request` import that only it used.
- `backend/services/explainability_service.py` — removed `get_predicted_class_index()` and
  `get_top_probability()` (defined but never called, internal or external).

---

## 5. Unused Imports / Duplicate Logging

- `backend/api/v1/chat.py` — removed duplicate `import logging` + `_logger` block at lines 199-200.
  The canonical `_logger` at line 28 remains and is used at lines 149 and 254.
- `backend/api/v1/recovery.py` — removed unused `RecoveryPlanCreate` import.

---

## 6. Dependency Changes

- `frontend/package.json` / `frontend/package-lock.json` — removed unused `nodemon` devDependency
  (no script referenced it; verified in both `package.json` and the lockfile). `npm install` updated the
  lockfile; `node_modules/nodemon` removed.

---

## 7. Verification Results

### Backend (`backend/` — local Python 3.14.4 venv)
- `python -m py_compile` on all 6 edited files: **OK**.
- `ruff check` on the 6 edited files: no **new** violations introduced (remaining findings are
  pre-existing repo-wide style issues, e.g. `I001`, `B008`, `BLE001`, `UP045`, `F841` in code not
  touched by this phase).
- `pytest` (all service-level suites, 94 tests): **93 passed, 1 failed**.
  - The 1 failure, `tests/test_severity_service.py::test_classify_mild`
    (`classify("Mild Food Poisoning")` returns `Moderate` instead of `Mild`), is a **pre-existing**
    assertion failure in severity logic — no severity code was touched in this phase.
- `tests/test_predictions_api.py` could not be run cleanly locally: the known **pre-existing** native
  crash ("Windows fatal exception: access violation") on Python 3.14.4 in pymongo/chromadb background
  threads during GC, and the pre-existing SHAP `ExplainerError` (test mocks a 31-feature vector but the
  RF model has `n_features_in_ = 135`). Both predate Phase 3 and are unrelated to these changes; CI runs
  Python 3.11.

### Frontend (`frontend/`)
- `npm run test` — **135 tests passed** (20 test files). (Count changed from 138 because removed store
  members/tests and the dashboard store test rewrite removed 3 assertions.)
- `npm run lint` — **0 errors** (1 pre-existing warning in generated `coverage/` output, not source).
- `npm run build` — **succeeded** (exit 0).

---

## 8. Intentionally Skipped / Reported (not deleted)

| Item | Why skipped |
|---|---|
| `backend/bin/audit.py`, `backend/bin/startup_check.py` (P1 #13) | Medium confidence; not verified against the live deploy pipeline (Render). `startup_check.py` still references `ml/prompts/chat.txt`, so `chat.txt` is also retained. |
| `utils/settings.py` dead config vars (P1 #24) | Medium confidence; RAG/embeddings swap planned and infra reads cannot be fully confirmed. |
| Frontend `.env.local` PostHog/Sentry vars | Medium confidence; external infra reads. |
| `api/v1/recovery.py` `from typing import Optional, List` (line 3) | Pre-existing unused-import lint finding; flagged by ruff as `F401`. Left in place because it was pre-existing, not introduced here, and was not part of the verified P1 list. |
| `test_predictions_api.py` SHAP mock/model mismatch | Pre-existing test defect; not a Phase 3 scope item. |
| `test_severity_service.py::test_classify_mild` assertion | Pre-existing severity-classification discrepancy; not a Phase 3 scope item. |

---

## 9. Phase 2 Recap (P0 fixes, prior phase)

For reference, Phase 2 completed the following (a dedicated `PHASE2_P0_RESULTS.md` was requested but not
written; summarized here):
- Moved `@vitest/coverage-v8` to `frontend/package.json` (single declaration matching `vitest`); root
  `package.json` now has empty devDependencies. `npm run test:coverage` passes with v8 provider
  (138 tests; thresholds met: statements 94.11, branches 87.5, functions 97.29, lines 98.38).
- Aligned frontend `ShapExplanation` to backend (`{ base_value, feature_values }` with optional
  `relative_contribution_pct`). Backend unchanged (intentional API output).
- Aligned frontend `RiskScoreAnalytics` to backend (`{ current_score, category, last_computed }`).
  Backend unchanged.
