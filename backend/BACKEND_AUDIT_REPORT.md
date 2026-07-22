# Backend Audit Report

> **Generated:** 2026-07-22
> **Scope:** All Python files in `backend/`
> **Auditor:** Automated code analysis

---

## 1. Deleted Files

| File | Reason |
|---|---|
| `backend/models/__init__.py` | Empty module — no model classes ever defined; no imports found |
| `backend/models/` (directory) | Orphaned directory — nothing referenced it |
| `backend/utils/security_headers.py` | Unused — import was already removed from `main.py`; logic duplicated via middleware |

## 2. Bugs Fixed

### 2.1 CORS default missing `localhost:3001` ← **Hotfix**
**File:** `backend/utils/settings.py:27`
**Change:** `"http://localhost:3000,https://symptomscope.vercel.app"` → `"http://localhost:3000,http://localhost:3001,https://symptomscope.vercel.app"`
**Impact:** Frontend on port 3001 (staging/dev) would get CORS blocked on fresh deployment if `CORS_ORIGINS` env var wasn't explicitly set.

### 2.2 Dead field reference in `ChatRepository.add_message()`
**File:** `backend/repositories/chat_repository.py:76`
**Change:** `message.get("_original_session_id") or session_id` → `session_id`
**Impact:** `_original_session_id` was never set in the message dict, so `get()` always returned `None` and the `or session_id` fallback was always used. Dead code that was technically harmless but misleading.

### 2.3 Dead field reference in `ReminderRepository.log_status()`
**File:** `backend/repositories/reminder_repository.py:95`
**Change:** `log_entry.get("_original_id", reminder_id)` → `reminder_id`
**Impact:** Same pattern — `_original_id` never set, always fell back to `reminder_id`. Dead code removed.

## 3. Dead Code Detected (Not Removed)

These are functions/methods that exist in the codebase but are never called from any route or service:

| File | Dead Function | Notes |
|---|---|---|
| `services/prediction_service.py` | `get_predicted_class_index()` | Internal helper defined but never used; only `predict()` is called |
| `services/explainability_service.py` | `get_predicted_class_index()` | Same pattern — defined but unused; only `build_contributing_symptoms()` is called |
| `services/explainability_service.py` | `get_top_probability()` | Defined but unused |
| `repositories/risk_score_repository.py` | `get_all_scores_for_user()` | Never called; only `get_latest_score()`, `get_score_history()`, `create_or_update_score()` are used |
| `services/doctor_service.py` | `explain_recommendation()` | Never called by any route or service |
| `services/hospital_service.py` | `explain_recommendation()` | Never called by any route or service |
| `services/severity_service.py` | `get_all_disease_severities()` | Never called; only `classify()` is used |
| `services/precaution_service.py` | `get_precautions_with_priority()` | Never called; only `get_precautions()` is used |
| `services/symptom_search_service.py` | `get_by_category()` | Never called; categories are served via `get_categories()` |
| `utils/settings.py` | `cors_origins_list` (property) | Property defined but never read by any code — CORS middleware reads the raw string via `.split(",")` inline in `main.py` |
| `services/search_service.py` | `score_and_sort()` | The double-sort approach (`sorted(..., key=score_and_sort)`) is confusing but works — refactored to use a named inner function for clarity |

**Recommendation:** These are low-risk to leave; removing them provides negligible reduction in binary size. Consider cleaning them up during a dedicated refactoring sprint.

## 4. Code Cleanup Actions

| Action | Detail |
|---|---|
| `backend/models/` deleted | Empty stub with no references |
| `backend/utils/security_headers.py` deleted | Already removed from imports |
| Theme consolidation | `next-themes` removed from `package.json`; 3 dashboard pages + `sonner.tsx` migrated to zustand `@/lib/stores/theme-store` |
| Port standardization | All 5 API client files (`frontend/lib/`) use `http://localhost:8080` |
| Doc fixes | All 4 doc files updated from port 8000 to 8080 |
| `.env.example` CORS fix | Default CORS origins now include `:3001` |

## 5. Architecture Assessment

### Strengths
- Clean layered architecture: `api/v1/` → `services/` → `repositories/` → MongoDB
- Thread-safe ML model loading with `threading.Lock` + `TModelCache`
- Comprehensive CSP split: relaxed for `/docs`, strict for API routes
- Rate limiting on every endpoint
- Consistent auth via Clerk JWT middleware
- Good test coverage on core services (13 test files)

### Weaknesses
- Doctor/hospital data hardcoded in Python dicts — no DB, no CRUD
- ML models trained on synthetic data only — not clinically validated
- Chat LLM + Email SMTP are optional — silently degraded when unconfigured
- Analytics cache is in-memory — lost on restart, not shared across instances
- No pagination on list endpoints — only `limit` query param
- Test suite requires real MongoDB — no in-memory mock

## 6. File Count Summary

| Category | Count |
|---|---|
| Route files (`api/v1/`) | 10 |
| Services | 18 |
| Repositories | 4 |
| Schemas | 9 |
| Utils | 7 |
| Auth | 1 |
| Test files | 13 |
| ML models | 4 |
| ML training | 1 |
| Top-level Python | 2 (`main.py`, `pytest.ini`) |
| **Deleted** | **1 directory, 2 files** |

## 7. Key Metrics

| Metric | Value |
|---|---|
| Total Python files (post-cleanup) | ~65 |
| Lines of Python code | ~5,800 |
| API endpoints | 24 |
| MongoDB collections | 7 |
| ML diseases | 15 |
| Hardcoded doctors | 8 (Punjab-only) |
| Hardcoded hospitals | 8 (Punjab-only) |
| Test files | 13 |
| Unused functions (low-risk) | 9 |
