# SymptomScope AI — Complete Architecture Guide

---

## 1. Project Overview

### 1.1 Purpose

SymptomScope AI is an AI-powered healthcare intelligence platform that enables users to input symptoms through a multi-step wizard and receive ML-driven disease predictions, explainable AI insights, severity classification, emergency detection, doctor/hospital recommendations, and longitudinal health analytics.

### 1.2 Complete System Architecture

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                         FRONTEND (Next.js 16)                           │
 │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌─────────────────────┐ │
 │  │  Landing │  │    Symptom   │  │  Results │  │  Dashboard / History│ │
 │  │  Page    │  │    Checker   │  │  Page    │  │  Reports / Settings  │ │
 │  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └──────────┬──────────┘ │
 │       │               │               │                    │            │
 │       ▼               ▼               ▼                    ▼            │
 │  ┌──────────────────────────────────────────────────────────────────┐   │
 │  │             TanStack Query API Layer  |  Zustand Stores          │   │
 │  │   predictions.ts · stores/dashboard-store.ts · stores/theme-store│   │
 │  └─────────────────────────────────┬────────────────────────────────┘   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTPS + Bearer JWT
                                     ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                          BACKEND (FastAPI)                               │
 │  ┌──────────────────────────────────────────────────────────────────┐   │
 │  │  API Routes (api/v1/)                                            │   │
 │  │  predict.py · doctors.py · reports.py · symptoms.py              │   │
 │  │  hospitals.py · analytics.py · export.py                         │   │
 │  └────────────────────────┬─────────────────────────────────────────┘   │
 │                           │                                              │
 │  ┌────────────────────────▼─────────────────────────────────────────┐   │
 │  │  Services Layer                                                   │   │
 │  │  PredictionService · FeatureEngineeringService · SeverityService  │   │
 │  │  PrecautionService · EmergencyService · DoctorService             │   │
 │  │  HospitalService · ExplainabilityService · AnalyticsService       │   │
 │  │  ReportService · ReportExportService                              │   │
 │  └────────────────────────┬─────────────────────────────────────────┘   │
 │                           │                                              │
 │  ┌────────────────────────▼─────────────────────────────────────────┐   │
 │  │  ML Models (in-process, joblib-cached)                            │   │
 │  │  Decision Tree  +  Random Forest  +  LabelEncoder                 │   │
 │  │  SHAP TreeExplainer  +  SymptomColumns                            │   │
 │  └────────────────────────┬─────────────────────────────────────────┘   │
 │                           │                                              │
 │  ┌────────────────────────▼─────────────────────────────────────────┐   │
 │  │  Repository Layer (Motor async MongoDB)                           │   │
 │  │  PredictionRepository · (future repositories added per feature)   │   │
 │  └──────────────────────────────────────────────────────────────────┘   │
 └─────────────────────────┬───────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                  ▼
   ┌────────────┐    ┌────────────┐    ┌────────────┐
   │   Clerk    │    │   Sentry   │    │  PostHog   │
   │   Auth     │    │ Monitoring │    │ Analytics  │
   └────────────┘    └────────────┘    └────────────┘
```

### 1.3 Component Interactions

| Component | Communicates With | Protocol / Mechanism |
|-----------|-------------------|---------------------|
| Next.js Pages | TanStack Query → FastAPI Routes | HTTPS REST + Bearer JWT |
| FastAPI Routes | Services (DI via `Depends()`) | In-process Python calls |
| Services | ML Models (joblib lazy-load) | In-memory inference, thread-safe cache |
| Services | MongoDB (Motor async driver) | Async MongoDB Wire Protocol |
| ExplainabilityService | SHAP TreeExplainer | In-process TreeExplainer on RF model |
| Auth Middleware | Clerk JWKS endpoint | HTTPS / JWKS public key fetch |
| AnalyticsService | In-memory cache | `dict` + `Lock` for TTL-based caching |
| Frontend State | Zustand stores | Client-side reactive state |
| Form State | React Hook Form + Zod | Client-side validation |
| Monitoring | Sentry SDK | Error tracking via `capture_exception` |
| Product Analytics | PostHog JS | Page views, events |

---

## 2. Current Project Structure

### 2.1 Directory Layout

```
Symptom Scope AI/
├── backend/
│   ├── main.py                     # FastAPI app: middlewares, lifespan, router includes
│   ├── Dockerfile                  # Python 3.13-slim, uvicorn
│   ├── requirements.txt            # fastapi, motor, pydantic, shap, joblib, etc.
│   ├── .env / .env.example         # MongoDB URI, Clerk JWKS, CORS, Sentry, Redis
│   ├── api/v1/                     # Route modules
│   │   ├── predict.py              # POST /predict — main ML orchestration
│   │   ├── doctors.py              # GET /doctors, /specialties, /locations
│   │   ├── reports.py              # GET /reports/{user_id}
│   │   ├── symptoms.py             # GET /symptoms/search, /categories, /symptoms
│   │   ├── hospitals.py            # GET /hospitals, /locations
│   │   ├── analytics.py            # GET /analytics/{user_id}?range=
│   │   └── export.py               # GET /export/csv|pdf/{user_id}
│   ├── services/                   # Business logic & ML
│   │   ├── prediction_service.py   # DT + RF ensemble inference
│   │   ├── feature_engineering.py  # Symptom → binary vector (24 symptoms)
│   │   ├── severity_service.py     # Severity classification + escalation
│   │   ├── precaution_service.py   # Disease → precaution mapping
│   │   ├── emergency_service.py    # Emergency detection logic
│   │   ├── doctor_service.py       # Doctor DB + ranking algorithm
│   │   ├── hospital_service.py     # Hospital search + filter
│   │   ├── explainability_service.py # SHAP TreeExplainer
│   │   ├── analytics_service.py    # Health trends + TTL cache
│   │   ├── report_service.py       # Report aggregation
│   │   ├── report_export_service.py # CSV / PDF generation (reportlab)
│   │   └── disease_registry.py     # 16 diseases with full metadata
│   ├── schemas/                    # Pydantic request/response models
│   │   ├── prediction_schema.py
│   │   ├── doctor_schema.py
│   │   ├── hospital_schema.py
│   │   ├── analytics_schema.py
│   │   └── report_schema.py
│   ├── repositories/               # Data access layer (MongoDB CRUD)
│   │   └── prediction_repository.py
│   ├── auth/
│   │   └── dependency.py           # Clerk JWT verification (JWKS)
│   ├── utils/                      # Cross-cutting infrastructure
│   │   ├── settings.py             # Pydantic Settings (env vars)
│   │   ├── database.py             # Motor client + index setup
│   │   ├── rate_limit.py           # SlowAPI limiter
│   │   ├── security_headers.py     # Security headers middleware
│   │   ├── request_logger.py       # Request logging middleware
│   │   ├── logging_config.py       # JSON logging config
│   │   ├── exceptions.py           # Global exception handler
│   │   ├── env_check.py            # Startup env validation
│   │   └── monitoring.py           # Sentry initialization
│   ├── ml/
│   │   ├── models/                 # .pkl files (DT, RF, encoder, columns)
│   │   └── training/
│   │       └── train_models.py     # Model training script
│   └── tests/                      # pytest tests for all services + API
│
├── frontend/
│   └── src/
│       ├── app/                    # Next.js App Router pages
│       │   ├── layout.tsx          # Root layout + theme script
│       │   ├── page.tsx            # Landing page
│       │   ├── providers.tsx       # Clerk, Query, Sentry, PostHog, Theme
│       │   ├── middleware.ts       # Clerk route protection
│       │   ├── globals.css         # Tailwind + shadcn tokens
│       │   ├── symptom-checker/page.tsx  # Multi-step wizard
│       │   ├── results/page.tsx         # Prediction results + emergency panel
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   └── signup/page.tsx
│       │   └── (dashboard)/
│       │       ├── layout.tsx           # Sidebar + header shell
│       │       ├── dashboard/page.tsx    # Analytics dashboard
│       │       ├── history/page.tsx      # Prediction timeline
│       │       ├── reports/page.tsx      # Reports + export
│       │       └── settings/page.tsx     # Theme + Clerk profile
│       ├── components/
│       │   ├── ui/                 # shadcn/ui primitives
│       │   ├── layouts/            # DashboardHeader, DashboardSidebar
│       │   └── features/           # Business components
│       │       ├── symptom-selection-step.tsx
│       │       ├── details-step.tsx
│       │       ├── analyzing-step.tsx
│       │       ├── prediction-results.tsx
│       │       ├── emergency-action-panel.tsx
│       │       ├── doctor-recommendation-card.tsx
│       │       ├── step-indicator.tsx
│       │       ├── dashboard/          # 12 sub-components
│       │       ├── reports/            # 5 sub-components
│       │       └── history/            # 1 sub-component
│       ├── lib/
│       │   ├── api/predictions.ts # All API calls + TS interfaces
│       │   ├── stores/             # Zustand stores
│       │   │   ├── theme-store.ts
│       │   │   └── dashboard-store.ts
│       │   ├── validations/        # Zod schemas
│       │   └── utils.ts            # cn() helper
│       └── test/                   # Vitest setup
│
├── docs/                           # Project documentation
├── scripts/                        # deploy.sh, setup-local.sh
├── .github/workflows/              # CI/CD (backend-ci, frontend-ci, deploy)
├── docker-compose.yml
├── railway.json
└── package.json
```

### 2.2 Backend Layered Architecture

```
Client Request
      │
      ▼
 ┌────────────┐   Rate Limit, Security Headers,
 │ Middleware  │   Request Logging, CORS, Size Check
 └─────┬──────┘
       │
 ┌─────▼──────┐   Clerk JWT → user_id (auth/dependency.py)
 │ Auth Layer  │
 └─────┬──────┘
       │
 ┌─────▼──────┐   Pydantic validation (schemas/)
 │ API Route   │
 │ (e.g. predict) │
 └─────┬──────┘
       │
 ┌─────▼──────────────┐   All services injected via Depends()
 │ Services Layer     │
 │ PredictionService   │────> joblib DT + RF models
 │ SeverityService     │────> disease_registry.py
 │ EmergencyService    │────> confidence + severity thresholds
 │ DoctorService       │────> in-memory doctor DB
 │ ExplainabilityService│───> SHAP TreeExplainer
 │ AnalyticsService    │────> in-memory TTL cache
 └─────┬──────────────┘
       │
 ┌─────▼──────────────┐   async Motor, MongoDB Atlas
 │ Repository Layer   │
 │ PredictionRepository│──> predictions collection
 └────────────────────┘
```

**Key patterns:**
- **Dependency injection**: All services resolved via FastAPI's `Depends()` — no manual wiring
- **ML model lifecycle**: Models loaded lazily on first call via `@property` with thread-safe double-checked locking (`_cache_lock`)
- **Caching**: Analytics cached in `dict` with 60s TTL; cache invalidated on new prediction
- **Static data**: Doctors, hospitals, symptoms, disease registry stored in-memory (no DB for these)
- **Rate limiting**: SlowAPI at 10 requests/minute per endpoint

### 2.3 Frontend Architecture

```
Page Components (App Router)
     │
     ├── /                → Landing (SSR, public)
     ├── /symptom-checker → Multi-step wizard (CSR, protected)
     ├── /results         → Prediction display (CSR, protected)
     └── /(dashboard)     → Route group (CSR, Clerk middleware)
          ├── /dashboard  → Analytics + charts
          ├── /history    → Prediction timeline
          ├── /reports    → Report generation + export
          └── /settings   → Theme + user profile

State Architecture:
  ┌──────────────────────────────────────────────────────┐
  │   Server State: TanStack Query                       │
  │   - Automatic caching, dedup, retry, stale-while-revalidate  │
  │   - Keys: ['prediction', ...], ['analytics', userId, range]  │
  ├──────────────────────────────────────────────────────┤
  │   Client State: Zustand                              │
  │   - theme-store: dark/light mode                     │
  │   - dashboard-store: selectedTimeRange (1m/3m/6m/1y)│
  ├──────────────────────────────────────────────────────┤
  │   Form State: React Hook Form + Zod                  │
  │   - symptom-form: symptoms[], age, gender, etc.     │
  └──────────────────────────────────────────────────────┘

UI Layer:
  ┌──────────────────────────────────────────────────────┐
  │   shadcn/ui (Radix primitives + Tailwind v4)         │
  │   Framer Motion (page transitions, step animations)  │
  │   Recharts (dashboard charts, trends)                │
  │   Lucide React (icons throughout)                    │
  └──────────────────────────────────────────────────────┘

API Layer:
  ┌──────────────────────────────────────────────────────┐
  │   lib/api/predictions.ts                             │
  │   - All fetch calls with auth headers                │
  │   - Full TypeScript interfaces for all responses     │
  │   - Base URL: NEXT_PUBLIC_API_URL                    │
  └──────────────────────────────────────────────────────┘
```

---

## 3. Current Application Routes

| Route | Purpose | Components | Backend APIs | Data Flow | UI/UX |
|-------|---------|------------|-------------|-----------|-------|
| `/` | Marketing landing page | HeroSection, FeaturesSection, HowItWorksSection, Footer, Header | None static | No auth banner with CTA to `/symptom-checker` | |
| `/symptom-checker` | Multi-step symptom input wizard | StepIndicator, SymptomSelectionStep, DetailsStep, AnalyzingStep, PredictionResults | `POST /api/v1/predict` | User selects symptoms → fills details → mutation to predict → redirect to `/results?symptoms=...` | 4 animated steps, searchable symptom picker, real-time form validation |
| `/results` | Display prediction with all results | PredictionResults, EmergencyActionPanel, DoctorRecommendationCard | `POST /api/v1/predict` (via query) | Reads `symptoms` from URL searchParams → calls predict → renders cards | Animated entrance, severity badge, confidence gauge, SHAP bars, doctor cards, emergency alert |
| `/(dashboard)/dashboard` | Health analytics overview | DashboardAnalyticsContent (12 sub-components), SummaryCards, Charts, TimeRangeSelector | `GET /api/v1/analytics/{user_id}?range=`, `GET /api/v1/reports/{user_id}` | Fetch analytics + report for selected range → render grid of charts | Time-range filter tabs, summary cards, disease/severity/symptom charts, health insights |
| `/(dashboard)/history` | Prediction timeline | HistoryChartContent, SymptomTimeline | `GET /api/v1/reports/{user_id}`, `GET /api/v1/analytics/{user_id}?range=6m` | Fetch all predictions → render chronological list + trend chart | Timeline with severity badges, symptom tags, monthly trends |
| `/(dashboard)/reports` | Report generation + export | ReportsChartContent, ReportSummary, ReportCharts, ReportExport | `GET /api/v1/reports/{user_id}`, `GET /api/v1/export/csv/{user_id}`, `GET /api/v1/export/pdf/{user_id}` | Fetch report → display summary + click export → browser download | Executive summary, prediction history table, PDF/CSV download buttons |
| `/(dashboard)/settings` | User preferences | UserProfile (Clerk), ThemeToggle | None client-side | Clerk-managed profile form, Zustand theme store | Dark/light toggle, full Clerk UserProfile component |
| `/(auth)/login` | Clerk sign-in | Clerk `<SignIn />` | Clerk-managed | Redirect to Clerk hosted UI or embedded form | Clerk default UI |
| `/(auth)/signup` | Clerk sign-up | Clerk `<SignUp />` | Clerk-managed | Same as login | Clerk default UI |

---

## 4. Backend API Documentation

### 4.1 Endpoint Summary

| # | Method | Path | Auth | Rate Limit | Purpose | Frontend Consumer |
|---|--------|------|------|------------|---------|-------------------|
| 1 | POST | `/api/v1/predict` | Bearer | 10/min | ML prediction (DT + RF + SHAP) | `/symptom-checker`, `/results` |
| 2 | GET | `/api/v1/doctors` | Bearer | 10/min | Search/recommend doctors | PredictionResults (embedded), (future doctor search page) |
| 3 | GET | `/api/v1/doctors/specialties` | Bearer | 10/min | List all specialties | Future filter dropdowns |
| 4 | GET | `/api/v1/doctors/locations` | Bearer | 10/min | List all locations | Future filter dropdowns |
| 5 | GET | `/api/v1/reports/{user_id}` | Bearer* | 10/min | Aggregated report + all predictions | `/dashboard`, `/history`, `/reports` |
| 6 | GET | `/api/v1/symptoms/search` | Bearer | 10/min | Fuzzy symptom search | `/symptom-checker` search input |
| 7 | GET | `/api/v1/symptoms/categories` | Bearer | 10/min | Symptom categories | `/symptom-checker` filter |
| 8 | GET | `/api/v1/symptoms` | Bearer | 10/min | All symptoms list | `/symptom-checker` |
| 9 | GET | `/api/v1/hospitals` | Bearer | 10/min | Hospital search + filter | EmergencyActionPanel (dialog) |
| 10 | GET | `/api/v1/hospitals/locations` | Bearer | 10/min | Hospital locations | Future filter |
| 11 | GET | `/api/v1/analytics/{user_id}` | Bearer* | 10/min | Full analytics with charts data | `/dashboard`, `/history`, `/reports` |
| 12 | GET | `/api/v1/export/csv/{user_id}` | Bearer* | 10/min | CSV export of predictions | `/reports` download button |
| 13 | GET | `/api/v1/export/pdf/{user_id}` | Bearer* | 10/min | PDF export of predictions | `/reports` download button |
| 14 | GET | `/health` | None | — | Health check | None (monitoring) |

*\* Also verifies `auth_user_id == user_id` (ownership check)*

### 4.2 Detailed Specifications

#### `POST /api/v1/predict`

**Request:**
```json
{
  "symptoms": ["fever", "dry_cough", "fatigue"],
  "age": 35,
  "gender": "male",
  "existing_conditions": ["hypertension"],
  "symptom_duration": "3 days",
  "pain_level": 5
}
```

**Services used:** FeatureEngineeringService, PredictionService, SeverityService, PrecautionService, EmergencyService, DoctorService, ExplainabilityService, PredictionRepository

**Business logic (in order):**
1. Encode `symptoms` → binary vector (24 symptom positions)
2. Ensemble predict: `(DT_probs + RF_probs) / 2` → top 3 diseases + confidence
3. Classify severity: base from registry, check escalation threshold
4. Get precautions: disease-specific + severity fallback
5. Detect emergency: `Severe` severity OR high-confidence critical disease OR escalation
6. Recommend specialist + top 3 doctors by composite score (specialty 50% + location 25% + rating 15% + query 10%)
7. SHAP explanation via `TreeExplainer` → top 5 contributing symptoms with shap_values
8. Save `PredictionRecord` to MongoDB `predictions` collection
9. Invalidate analytics cache for user

**Response**: Full `PredictionResponse` with prediction, alternatives, severity, SHAP, doctors, emergency info, explanation summary

**Database interaction:** `insert_one` into `predictions` collection

---

#### `GET /api/v1/analytics/{user_id}?range=6m`

**Query params:** `range` ∈ {`1m`, `3m`, `6m`, `1y`} (default: `6m`)

**Services:** AnalyticsService, PredictionRepository

**Business logic:**
1. Check in-memory cache for `{user_id}:{range}` key (TTL: 60s)
2. Cache hit → return immediately
3. Cache miss → fetch predictions from DB filtered by time range
4. Compute: summary stats, disease frequency, severity breakdown, monthly trends, symptom insights/trends, confidence trends, recurring conditions, health summary, insights text
5. Store in cache → return

**Database interaction:** `find_by_user(user_id, time_range)` → `predictions` collection with timestamp filter, sorted descending, limit 100

**Frontend consumers:** Dashboard, History, Reports pages

---

#### `GET /api/v1/reports/{user_id}`

**Services:** ReportService, PredictionRepository

**Business logic:** Fetch ALL predictions for user → compute summary (total, most common disease, avg confidence, severity distribution) → return with full prediction list

**Database interaction:** `find_by_user(user_id)` — no time filter, unlimited

---

#### `GET /api/v1/doctors?specialty=&location=&q=&sort_by=&sort_order=&limit=`

**Services:** DoctorService

**Business logic:**
1. Filter by specialty/location if provided
2. Score each doctor: specialty match (50%) + location match (25%) + rating (15%) + query relevance (10%)
3. Sort by composite score (default) or by rating/distance/availability
4. Return top N (default 50)

**Data source:** In-memory list of 8 doctors (hardcoded in `doctor_service.py`)

---

#### `GET /api/v1/hospitals?emergency_only=&specialty=&location=&sort_by=&limit=`

**Services:** HospitalService (follows same pattern as DoctorService)

**Data source:** In-memory list of hospitals

---

#### `GET /api/v1/export/csv/{user_id}` / `GET /api/v1/export/pdf/{user_id}`

**Services:** ReportExportService (reportlab for PDF, csv stdlib for CSV)

**Response:** Binary file download (`Content-Disposition: attachment`)

**Business logic:** Fetch all user predictions → generate formatted document

---

## 5. Complete Existing User Flow

```
┌──────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────┐
│  LANDING │───▶│ AUTHENTICATE │───▶│ SYMPTOM CHECKER │───▶│ PREDICTION  │
│  PAGE    │    │ (Clerk)      │    │ 4-step wizard   │    │ (ML Engine) │
└──────────┘    └──────────────┘    └─────────────────┘    └──────┬──────┘
                                                                  │
                                                                  ▼
                    ┌──────────────────────────────────────────────┐
                    │         PREDICTION ORCHESTRATION             │
                    │                                              │
                    │  1. FeatureEngineeringService                 │
                    │     symptoms → binary vector (24 features)   │
                    │                                              │
                    │  2. PredictionService                         │
                    │     DT_probs + RF_probs → avg → top 3        │
                    │                                              │
                    │  3. ExplainabilityService (SHAP)              │
                    │     TreeExplainer → top 5 symptoms + values   │
                    │                                              │
                    │  4. SeverityService                           │
                    │     registry base + confidence escalation     │
                    │                                              │
                    │  5. EmergencyService                          │
                    │     severity + confidence + disease risk      │
                    │                                              │
                    │  6. DoctorService + HospitalService           │
                    │     specialist + top 3 doctors                │
                    │                                              │
                    │  7. PredictionRepository                      │
                    │     save to MongoDB + invalidate cache        │
                    └──────────────────────────────────────────────┘
                                    │
                                    ▼
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │  RESULTS │───▶│DASHBOARD │───▶│ HISTORY  │───▶│ REPORTS  │───▶│ EXPORT   │
 │  page    │    │analytics │    │timeline  │    │summary   │    │PDF/CSV   │
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

**Detailed step-by-step data movement:**

1. **Landing Page → Auth**: User visits `/`. Clicks "Get Started". Clerk redirects to `/signup` or `/login`. After auth, redirects to `/symptom-checker`.

2. **Symptom Checker → Prediction**: User completes 4 steps:
   - Step 1: Select symptoms from searchable list (fetched via `GET /symptoms/search`)
   - Step 2: Fill demographics (age, gender, existing conditions, duration, pain level)
   - Step 3: "Analyzing" animated loading state
   - Step 4: Mutation fires `POST /api/v1/predict` with `{symptoms, age, gender, existing_conditions, symptom_duration, pain_level}` + Bearer token

3. **Backend ML Pipeline** (inside a single FastAPI request handler):
   - `FeatureEngineeringService.encode_symptoms()` → numpy array of 0s/1s (24 positions)
   - `PredictionService.predict()` → DT/RF ensemble → `PredictionResult` with top disease, confidence (%), alternatives, feature importances
   - `ExplainabilityService.build_contributing_symptoms()` → SHAP `TreeExplainer` → base_value + top 5 symptoms with shap_values and contribution percentages
   - `SeverityService.classify()` → Mild/Moderate/Severe from registry + optional escalation
   - `PrecautionService.get_precautions()` → list of precaution strings for that disease+severity
   - `EmergencyService.detect()` → bool + reasons (Severe severity triggers, or confidence > 90% for emergency-risk diseases, or escalation thresholds)
   - `DoctorService.get_recommendations()` → composite-scored ranked doctors
   - `PredictionRepository.create()` → `insert_one` to MongoDB `predictions` collection
   - `invalidate_user_cache()` → clear analytics cache entries for this user

4. **Results Page**: Receives full `PredictionResponse`. Renders:
   - Emergency banner (if applicable) with "Call Ambulance" / "Nearby Hospitals" / "Teleconsultation" buttons
   - Disease name + confidence % + severity badge
   - Alternative possibilities (badges)
   - SHAP top contributing symptoms (horizontal bars with percentage)
   - Precautions list
   - Doctor recommendations (cards with avatar, specialty, rating, distance, availability)
   - Medical disclaimer
   - Actions: "Check New Symptoms" or "Go to Dashboard"

5. **Dashboard**: User navigates to `/dashboard`. Components call:
   - `GET /api/v1/reports/{user_id}` → all predictions
   - `GET /api/v1/analytics/{user_id}?range=6m` → full analytics
   - Renders 12 sub-components: SummaryCards, HealthSummaryBanner, DiseaseChartsRow, TrendChartsRow, SymptomsConfidenceRow, SymptomTimeline, SymptomProgressTrends, RecurringConditions, HealthInsights, RecommendationHistory
   - User can switch time range via tabs (1m/3m/6m/1y), which calls analytics again with new range

6. **History**: User views `/history`. Shows chronological prediction list with severity badges, symptom tags, trend chart.

7. **Reports**: User views `/reports`. Shows executive summary + full prediction history. Click "Export CSV" → downloads CSV. Click "Export PDF" → downloads PDF.

8. **Settings**: User visits `/settings`. Toggles dark/light mode (Zustand + next-themes). Manages Clerk profile.

---

## 6. Three New Features

### 6.1 Feature 1: AI Health Chat Assistant

#### Why It Should Be Added
The existing platform provides static prediction results but lacks conversational follow-up. Users often have questions about their results — what symptoms to monitor, how precautions work, what alternative diagnoses mean. A chat assistant powered by an LLM provides immediate, context-aware answers using the user's actual prediction data, closing the educational gap without requiring a doctor visit.

#### Functional Requirements
- Floating chat widget accessible from any authenticated page
- Context-aware: receives current prediction, symptoms, severity, confidence, precautions
- Automatically opens on Results page with contextual greeting
- Educational-only responses with medical disclaimer in every message
- Message history stored per session
- Rate-limited to prevent abuse
- Uses OpenAI-compatible API (configurable endpoint + API key)
- Supports markdown rendering in responses
- Session timeout after 30 minutes of inactivity

#### User Workflow
1. User is on any authenticated page → sees floating chat bubble in bottom-right corner
2. Clicks bubble → widget expands showing chat history or welcome message
3. On Results page → widget auto-opens with "I see you're looking at [disease]. Would you like to know more about this condition?"
4. User types questions: "What symptoms should I watch for?", "How serious is this?", "What does SHAP importance mean?"
5. Backend receives message + prediction context → calls LLM API with structured system prompt → returns response
6. Chat history displayed in scrollable area with user/assistant bubbles
7. User can clear session or minimize widget

#### Required Backend Changes
- New service: `ChatService` in `backend/services/chat_service.py`
- New route: `backend/api/v1/chat.py` with `POST /api/v1/chat/session` and `POST /api/v1/chat/message`
- New dependency: `openai` or `httpx` for LLM API calls
- LLM API key and endpoint in `.env` settings
- System prompt builder that constructs context from prediction data
- Rate limiting at 5 messages/minute per user
- Session auto-expiry logic

#### Required Frontend Changes
- New component: `ChatWidget` (floating bubble + expandable panel)
- New component: `ChatMessage` (user/assistant message bubble)
- New component: `ChatInput` (text input with send button)
- Zustand store: `chat-store.ts` (session state, messages, open/closed)
- Integration in root layout or dashboard layout so widget is globally available
- Auto-open behavior on `/results` page (triggered when prediction data is available)
- Medical disclaimer banner at bottom of chat panel

#### New Database Collections/Tables
- `chat_sessions`: `{ _id, userId, startedAt, lastActivityAt, isActive, predictionContext (optional) }`
- `chat_messages`: `{ _id, sessionId, role (user/assistant), content, createdAt, metadata }`

#### New Services
- `ChatService`: creates sessions, sends messages to LLM, stores history, validates context
- `LlmClient`: thin wrapper around OpenAI-compatible API (configurable base URL, key, model)

#### New API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/chat/session` | Create new chat session (optionally with prediction_id for context) |
| POST | `/api/v1/chat/message` | Send message + get LLM response |
| GET | `/api/v1/chat/sessions` | List user's chat sessions |
| GET | `/api/v1/chat/messages/{session_id}` | Get message history for a session |

#### New Frontend Routes
- None (widget is global overlay, not a page)
- However, could add `/chat` standalone page for full-screen mode (optional low-priority)

#### Required UI Components
- `ChatWidget` — floating action button + slide-out panel
- `ChatMessage` — message bubble (user = right-aligned blue, assistant = left-aligned gray)
- `ChatInput` — textarea + send button + character limit
- `ChatSessionList` — list of previous sessions (in widget or settings)
- `MedicalDisclaimerBanner` — "This AI is for educational purposes only..."

#### Integration with Existing Prediction Flow
- When user receives a prediction on Results page, the frontend passes `prediction_id` to the chat widget
- Chat session creation includes prediction context: disease, symptoms, confidence, severity, precautions
- LLM system prompt includes this context so the assistant can answer questions specific to that prediction
- Analytics dashboard could surface "Ask AI about this trend" buttons

#### Security and Validation Considerations
- User message length limit: 500 characters
- Rate limit: 5 messages/minute per user (SlowAPI)
- LLM response timeout: 15 seconds
- All messages logged for abuse monitoring
- Medical disclaimer prepended to every assistant response
- API key stored server-side only (in `.env`)
- Session timeout: 30 min inactivity → auto-close
- Content filtering: reject messages with URLs, phone numbers, or personal health identifiers
- CORS and auth: same as existing API (Bearer token)

---

### 6.2 Feature 2: Medicine Reminder System

#### Why It Should Be Added
After receiving a prediction with severity and precautions, users often need to track medications (prescribed or OTC). A reminder system keeps users engaged with the platform beyond the initial prediction, provides ongoing value, and integrates naturally with the existing health tracking lifecycle. The document lists "Medication Reminder System" as a high-priority feature.

#### Functional Requirements
- Users manually add medicines with name, dosage, frequency, duration
- Reminders via in-app notification banner and email
- Schedule types: daily, specific days, every X hours, as-needed
- Reminder status tracking: active, completed, missed
- CRUD operations for reminders
- List view of all active reminders on dashboard
- Ability to link a reminder to a specific prediction (optional)
- Email reminders via SMTP (configurable in settings)
- Batch check every 5 minutes for due reminders

#### User Workflow
1. User receives a prediction on Results page → sees "Set Medicine Reminder" button
2. Clicks button → opens dialog with pre-filled medicine fields (optional, user can start from dashboard too)
3. User fills: medicine name, dosage (e.g., "500mg"), frequency, duration (e.g., "7 days"), start time
4. Saves → reminder appears in active reminders list
5. At scheduled time → in-app banner notification + email sent
6. User can mark as "Taken" or "Missed"
7. Dashboard shows "Active Reminders" card with status overview
8. User can edit, pause, or delete reminders

#### Required Backend Changes
- New service: `ReminderService` in `backend/services/reminder_service.py`
- New route: `backend/api/v1/reminders.py`
- New scheduler: lightweight background task (apscheduler or simple asyncio loop) to check due reminders every 5 minutes
- Email utility: `utils/email.py` for sending reminder emails via SMTP
- Settings update: add SMTP config, reminder check interval
- Invalidate any per-user cache when reminders change

#### Required Frontend Changes
- New route: `/reminders` under dashboard group
- New component: `ReminderList` — table/card list of all reminders
- New component: `ReminderForm` — create/edit dialog with form fields
- New component: `ReminderCard` — single reminder display with status badge
- New component: `ReminderDashboardCard` — active reminders summary for dashboard page
- Zustand store: `reminder-store.ts` (list, filters)
- In-app notification toast (using existing sonner toasts)
- "Set Reminder" button on Results page (after prediction)
- Dashboard integration: show next upcoming reminder

#### New Database Collections/Tables
- `medicine_reminders`: `{ _id, userId, medicineName, dosage, frequency, scheduleDetails, startDate, endDate, status, linkedPredictionId (optional), createdAt, updatedAt }`
- `reminder_logs`: `{ _id, reminderId, userId, status (taken/missed/skipped), timestamp, note }`

#### New Services
- `ReminderService`: CRUD for reminders, scheduling logic, status tracking
- `EmailService`: send email reminders via SMTP (configurable provider)

#### New API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/reminders` | List user's reminders (active/completed/all) |
| POST | `/api/v1/reminders` | Create new reminder |
| PUT | `/api/v1/reminders/{id}` | Update reminder |
| DELETE | `/api/v1/reminders/{id}` | Delete reminder |
| POST | `/api/v1/reminders/{id}/log` | Log taken/missed status |
| GET | `/api/v1/reminders/upcoming` | Get next due reminder for dashboard |

#### New Frontend Routes
- `/(dashboard)/reminders` — Full reminder management page
- (Optional modal/dialog version for quick access from results page)

#### Required UI Components
- `ReminderList` — paginated list with filters (active/completed/all)
- `ReminderForm` — dialog with fields: medicine name, dosage, frequency, duration, start time
- `ReminderCard` — card showing name, dosage, next dose time, status badge
- `ReminderStatusBadge` — Active/Completed/Missed with color coding
- `ReminderDashboardCard` — small card for dashboard showing next reminder
- `TakeMissedButtons` — inline action buttons on reminder card
- `EmailPreferenceToggle` — opt-in for email reminders

#### Integration with Existing Prediction Flow
- Results page shows "Set Medicine Reminder" button that auto-fills reminder with disease context
- Optional `linkedPredictionId` field links reminder to a specific prediction for reference
- Dashboard can show reminder compliance alongside health analytics
- PDF report could include active medicine reminders section

#### Security and Validation Considerations
- Dosage validation: numeric + unit (mg, ml, tablet, capsule, etc.)
- Frequency validation: must be a reasonable interval (not more than once per hour)
- Duration cap: max 365 days
- Email reminders opt-in only (user must toggle preference)
- Reminder count limit: max 50 active reminders per user
- No sensitive medical data in email subject lines (use generic "SymptomScope Reminder")
- Unsubscribe link in all reminder emails

---

### 6.3 Feature 3: Health Risk Score

#### Why It Should Be Added
The existing platform provides per-prediction results but lacks an aggregate health risk assessment. A Health Risk Score (0–100) consolidates prediction history, demographics, lifestyle factors, and severity into a single actionable metric. This gives users a quick health snapshot and tracks improvement/decline over time. The document explicitly mentions "Predictive health scoring" as a medium-priority feature.

#### Functional Requirements
- Risk score from 0 (lowest risk) to 100 (highest risk)
- Risk categories: Low (0–33), Medium (34–66), High (67–100)
- Inputs: age, gender, BMI, lifestyle (exercise, diet), smoking status, sleep duration, existing conditions, prediction history, disease severity
- Score recalculated on each new prediction
- Historical trend showing score changes over time
- Breakdown of contributing risk factors
- Displayed on Dashboard, Results page, and PDF health report
- Risk tips: actionable suggestions to lower risk score

#### User Workflow
1. User receives a prediction → risk score auto-calculated and displayed in results
2. User navigates to Dashboard → sees current risk score prominently in HealthSummaryBanner
3. Trend chart shows score over time (last 6 months)
4. Risk breakdown: pie/bar chart showing which factors contribute most
5. User can update profile (BMI, lifestyle, smoking, sleep) in Settings → risk score recalculates
6. PDF report includes risk score summary with trend

#### Required Backend Changes
- New service: `RiskScoreService` in `backend/services/risk_score_service.py`
- New route: `backend/api/v1/risk_score.py`
- Integration into prediction flow: after prediction saved, compute + save risk score
- Settings update: add risk score config (weights per factor)
- Update `AnalyticsResponse` to include risk score data
- Update `HealthSummary` model to include risk_score

#### Required Frontend Changes
- New route: none (integrated into existing Dashboard and Results)
- New component: `RiskScoreGauge` — gauge/circular progress showing 0–100 score
- New component: `RiskCategoryBadge` — Low/Medium/High badge
- New component: `RiskTrendChart` — line chart of score over time
- New component: `RiskFactorBreakdown` — horizontal bars for contributing factors
- New component: `RiskTips` — actionable suggestions
- Update `HealthSummaryBanner` to include risk score
- Update `PredictionResults` to show risk score
- Update PDF export to include risk score section
- Zustand store: update dashboard-store if needed for risk-specific filtering

#### New Database Collections/Tables
- `health_risk_scores`: `{ _id, userId, score, category, factorBreakdown, timestamp, linkedPredictionId (optional) }`
- `user_health_profile`: `{ _id, userId, age, gender, bmi, exerciseFrequency, dietType, smokingStatus, sleepHours, existingConditions, updatedAt }` (this can be an extension of user profile, stored alongside or in a new collection)

#### New Services
- `RiskScoreService`: compute risk score algorithm, factor breakdown, trend analysis, risk tips

#### Risk Score Algorithm (Custom)
```
Score = 0

// Age factor (0–15 points)
if age >= 60: score += 15
else if age >= 45: score += 10
else if age >= 30: score += 5

// BMI factor (0–10 points)
if bmi >= 30: score += 10
else if bmi >= 25: score += 5

// Lifestyle factor (0–10 points)
if exercise < 2/week: score += 5
if diet is "unhealthy" or "irregular": score += 5

// Smoking factor (0–15 points)
if current smoker: score += 15
if former smoker: score += 8

// Sleep factor (0–10 points)
if sleep < 5h or > 9h: score += 10
if sleep < 6h or > 8h: score += 5

// Existing conditions (0–20 points)
for each condition: score += 5 (max 20)

// Prediction history factor (0–20 points)
// Based on last 5 predictions
severe_count * 5 + moderate_count * 3 - mild_count * 1
clamped to 0–20

// Severity trend (0–10 points)
if most recent severity is Severe: score += 10
if most recent severity is Moderate: score += 5

// Normalize to 0–100
return min(score, 100)
```

#### New API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/risk-score` | Get current risk score + breakdown |
| GET | `/api/v1/risk-score/history?range=6m` | Get risk score trend over time |
| PUT | `/api/v1/risk-score/profile` | Update user health profile (BMI, lifestyle, etc.) |
| GET | `/api/v1/risk-score/profile` | Get current health profile |
| GET | `/api/v1/risk-score/tips` | Get actionable risk reduction tips |

#### New Frontend Routes
- None — all integrated into existing Dashboard, Results, and Reports pages
- Profile update via `/settings` page (add health profile section)

#### Required UI Components
- `RiskScoreGauge` — large circular gauge (0–100) with color zones
- `RiskCategoryBadge` — `Low` (green), `Medium` (yellow), `High` (red) badge
- `RiskTrendChart` — Recharts LineChart showing score over months
- `RiskFactorBreakdown` — horizontal stacked bars per factor
- `RiskTips` — card with bullet-point suggestions
- `HealthProfileForm` — form for BMI, exercise, diet, smoking, sleep (in Settings)

#### Integration with Existing Prediction Flow
- After prediction is saved in `POST /api/v1/predict`, compute risk score and save to `health_risk_scores`
- Risk score included in `PredictionResponse` (new field)
- Risk score included in `AnalyticsResponse` (new fields in Summary and HealthSummary)
- PDF report: new section "Health Risk Assessment" with gauge + trend
- Dashboard HealthSummaryBanner shows risk score prominently
- Setting a new health profile (BMI, lifestyle) triggers recalculation

#### Security and Validation Considerations
- BMI: range 10–60, validated
- Sleep hours: 1–24, validated
- Exercise frequency: 0–7 days/week
- Smoking status: enum (never, former, current)
- Profile data belongs to authenticated user only
- Risk score is informational only — disclaimer displayed alongside
- Score can be recalculated on demand, but auto-calculated on prediction and profile update

---

## 7. Updated Route Structure

```
/                                          [EXISTING] Landing page
/(auth)
  /login                                   [EXISTING] Clerk sign-in
  /signup                                  [EXISTING] Clerk sign-up

/symptom-checker                           [EXISTING] Multi-step wizard

/results                                   [EXISTING] Prediction results

/(dashboard)                               [EXISTING] Protected route group
  /dashboard                               [EXISTING] Analytics dashboard
    (RiskScoreGauge, RiskTrendChart added) [NEW UI]  Risk score widgets
    (ReminderDashboardCard added)          [NEW UI]  Next reminder

  /history                                 [EXISTING] Prediction timeline

  /reports                                 [EXISTING] Report + export
    (Risk score section added to PDF)      [NEW]     Enhanced reports

  /reminders                               [NEW]     Medicine reminder management
    (ReminderList, ReminderForm, logs)

  /settings                                [EXISTING] User preferences
    (HealthProfileForm added)              [NEW]     BMI, lifestyle, smoke, sleep
    (Email preference toggle added)        [NEW]     Reminder email settings

  /chat                                    [NEW] [optional] Full-screen chat

[Global overlay — no route, always available on authenticated pages]
  ChatWidget (floating bubble)             [NEW]     AI Health Chat Assistant
```

**Legend:**
- `[EXISTING]` — Already implemented
- `[NEW]` — Added as part of the three new features
- `[NEW UI]` — New components added to existing pages

---

## 8. Updated Backend APIs

### All APIs After Adding Three Features

**Existing APIs (unchanged):**

| Method | Path | Feature |
|--------|------|---------|
| POST | `/api/v1/predict` | Prediction |
| GET | `/api/v1/doctors` | Doctors |
| GET | `/api/v1/doctors/specialties` | Doctors |
| GET | `/api/v1/doctors/locations` | Doctors |
| GET | `/api/v1/reports/{user_id}` | Reports |
| GET | `/api/v1/symptoms/search` | Symptoms |
| GET | `/api/v1/symptoms/categories` | Symptoms |
| GET | `/api/v1/symptoms` | Symptoms |
| GET | `/api/v1/hospitals` | Hospitals |
| GET | `/api/v1/hospitals/locations` | Hospitals |
| GET | `/api/v1/analytics/{user_id}` | Analytics |
| GET | `/api/v1/export/csv/{user_id}` | Export |
| GET | `/api/v1/export/pdf/{user_id}` | Export |
| GET | `/health` | Health |

**New APIs (AI Health Chat Assistant):**

| Method | Path | Integration Point |
|--------|------|-------------------|
| POST | `/api/v1/chat/session` | Called when user opens chat widget. Optionally accepts `prediction_id` to load context. |
| POST | `/api/v1/chat/message` | Called on each user message. Calls LLM API with system prompt containing prediction context. |
| GET | `/api/v1/chat/sessions` | Lists user's chat sessions (for resuming or history view). |
| GET | `/api/v1/chat/messages/{session_id}` | Returns message history for a session (for widget rehydration). |

Integration: `ChatService` (new) → `LlmClient` (new, wraps OpenAI-compatible HTTP calls) → `chat_sessions` + `chat_messages` collections. Rate-limited at 5/min/user.

**New APIs (Medicine Reminder System):**

| Method | Path | Integration Point |
|--------|------|-------------------|
| GET | `/api/v1/reminders` | Fetches user's reminders (supports `status` filter). Consumed by ReminderList, ReminderDashboardCard. |
| POST | `/api/v1/reminders` | Creates new reminder. Called from ReminderForm dialog. Optionally links to `prediction_id`. |
| PUT | `/api/v1/reminders/{id}` | Updates reminder (edit dose, frequency, etc.). |
| DELETE | `/api/v1/reminders/{id}` | Deletes reminder. |
| POST | `/api/v1/reminders/{id}/log` | Logs Taken/Missed status. Consumed by TakeMissedButtons. |
| GET | `/api/v1/reminders/upcoming` | Returns next due reminder. Consumed by ReminderDashboardCard on Dashboard. |

Integration: `ReminderService` (new) → `medicine_reminders` + `reminder_logs` collections. Background scheduler (apscheduler or asyncio loop) checks every 5 min for due reminders → triggers `EmailService` (new) for email notifications and returns in-app data. Integrated into dashboard.

**New APIs (Health Risk Score):**

| Method | Path | Integration Point |
|--------|------|-------------------|
| GET | `/api/v1/risk-score` | Returns current risk score + factor breakdown. Consumed by Dashboard and Results. |
| GET | `/api/v1/risk-score/history?range=6m` | Returns score trend over time. Consumed by RiskTrendChart on Dashboard. |
| PUT | `/api/v1/risk-score/profile` | Updates user health profile (BMI, exercise, smoking, sleep). Called from HealthProfileForm in Settings. |
| GET | `/api/v1/risk-score/profile` | Returns current health profile (for form pre-fill). |
| GET | `/api/v1/risk-score/tips` | Returns personalized risk reduction tips based on factor breakdown. Consumed by RiskTips component. |

Integration: `RiskScoreService` (new) → `health_risk_scores` + `user_health_profile` collections. Auto-computed after each prediction (in `POST /api/v1/predict` handler). Score and breakdown included in expanded `PredictionResponse` + `AnalyticsResponse`. Profile data editable via Settings page.

**Modified existing APIs:**

| Method | Path | Change |
|--------|------|--------|
| POST | `/api/v1/predict` | Add `health_risk_score` field to response. After saving prediction, call `RiskScoreService.compute()` and save result. |
| GET | `/api/v1/analytics/{user_id}` | Include `current_risk_score` and `risk_score_history` in response. |
| GET | `/api/v1/reports/{user_id}` | Include risk score summary in report data (for PDF inclusion). |
| GET | `/api/v1/export/pdf/{user_id}` | Add risk score section to PDF template. |

---

## 9. Final End-to-End Application Flow

```
                         COMPLETE APPLICATION FLOW
                    (Existing + 3 New Features Integrated)

 REGISTRATION ─────────────────────────────────────────────────────────────
      │
      ▼
 1. User signs up via Clerk (Email / Google / OTP)
    → Redirected to Landing page or directly to Symptom Checker
    → Chat widget available (minimized)
    → No reminders yet
    → No risk score yet (insufficient data)
      │
      ▼
 2. LANDING PAGE → "Check Symptoms" CTA
      │
      ▼
 3. SYMPTOM CHECKER (4-step wizard)
    │
    ├─ Step 1: Select symptoms (search + filter)
    ├─ Step 2: Age, gender, existing conditions, duration, pain
    ├─ Step 3: Analyzing animation (loading state)
    └─ Step 4: Results page
      │
      ▼
 4. PREDICTION ORCHESTRATION (POST /api/v1/predict)
    │
    ├─ FeatureEngineeringService: symptoms → binary vector
    ├─ PredictionService: DT + RF ensemble → top 3 diseases
    ├─ ExplainabilityService (SHAP): top 5 contributing symptoms
    ├─ SeverityService: Mild/Moderate/Severe + escalation check
    ├─ EmergencyService: emergency detection (severity + confidence)
    ├─ DoctorService: specialist + top 3 doctor recommendations
    ├─ PredictionRepository: save to MongoDB
    │
    └─ NEW: RiskScoreService.compute() → save to health_risk_scores
         (Uses profile + prediction history + this prediction)
      │
      ▼
 5. RESULTS PAGE (full prediction display)
    │
    ├─ Primary prediction + confidence % + severity badge
    ├─ SHAP contributing symptoms (horizontal bars)
    ├─ Precautions list
    ├─ Doctor recommendation cards
    ├─ Emergency banner (if applicable) with action buttons
    │
    ├─ NEW: Health Risk Score gauge displayed
    │   └─ Score value + Low/Medium/High badge
    │
    ├─ NEW: "Set Medicine Reminder" button
    │   └─ Opens ReminderForm dialog (pre-filled with disease context)
    │
    ├─ NEW: Chat widget auto-opens with contextual greeting
    │   └─ "I see you're looking at [disease]. Ask me anything about it."
    │
    └─ Actions: "Check New Symptoms" | "Go to Dashboard"
      │
      ▼
 6. DASHBOARD (/dashboard)
    │
    ├─ Time-range filter tabs (1m/3m/6m/1y)
    ├─ Summary cards (total predictions, avg confidence, severe count)
    ├─ HealthSummaryBanner with risk level
    │   └─ NEW: RiskScoreGauge prominently displayed
    │
    ├─ Disease frequency + severity breakdown charts
    ├─ Monthly trend charts (disease + severity)
    ├─ Symptom insights + trends
    ├─ Confidence trends
    ├─ Recurring conditions list
    ├─ Health insights text
    │
    ├─ NEW: RiskTrendChart — score over time
    ├─ NEW: RiskFactorBreakdown — what contributes to risk
    ├─ NEW: RiskTips — actionable suggestions
    │
    └─ NEW: ReminderDashboardCard — next upcoming medicine
      │
      ▼
 7. HISTORY (/history)
    │
    ├─ Chronological prediction timeline
    ├─ Severity badges + symptom tags per entry
    └─ Monthly trend charts
      │
      ▼
 8. REMINDERS (/reminders) [NEW]
    │
    ├─ List of all active/completed reminders
    ├─ Create new reminder (form dialog)
    ├─ Edit/pause/delete reminders
    ├─ Mark Taken/Missed with note
    └─ Email preference toggle
      │
      ▼
 9. REPORTS (/reports)
    │
    ├─ Executive summary
    ├─ Full prediction history table
    ├─ NEW: Risk score summary section
    ├─ Export CSV → downloads
    └─ Export PDF → downloads (includes risk score + trend)
      │
      ▼
10. SETTINGS (/settings)
    │
    ├─ Dark/light mode toggle
    ├─ Clerk UserProfile (name, email, password)
    └─ NEW: HealthProfileForm
        ├─ BMI, exercise frequency, diet type
        ├─ Smoking status, sleep hours
        └─ Triggers risk score recalculation on save
      │
      ▼
11. CHAT WIDGET (global overlay) [NEW]
    │
    ├─ Available on all authenticated pages
    ├─ Context-aware (uses current prediction if on Results page)
    ├─ Ask about diseases, symptoms, precautions, SHAP
    ├─ Session history persisted
    ├─ Medical disclaimer in every response
    └─ 5 msg/min rate limit
      │
      ▼
12. LONG-TERM HEALTH MANAGEMENT
    │
    ├─ Each new prediction updates risk score
    ├─ Risk score trend shows improvement/decline
    ├─ Medicine adherence tracked via reminder logs
    ├─ Chat history provides ongoing education
    ├─ Dashboard becomes richer with more data
    ├─ PDF reports document full health journey
    └─ User can export complete history anytime
```

### How the Three Features Create a Cohesive Experience

| Phase | Existing Experience | With New Features |
|-------|-------------------|-------------------|
| **After prediction** | Static results page, user left with questions | Chat widget auto-opens with contextual answers. "Set Reminder" button visible. Risk score shows overall health snapshot. |
| **Daily use** | Only check symptoms when feeling ill | Reminders keep user returning. Chat answers quick questions. Risk score trend motivates healthy habits. |
| **Health tracking** | Prediction history + analytics | Now includes medicine adherence, risk score trends, lifestyle factors. Full picture of health journey. |
| **Report export** | Prediction data only | Includes risk score, factor breakdown, reminder compliance. More valuable for doctor visits. |
| **Engagement** | One-time prediction tool | Ongoing value: reminders, chat, risk tracking. Users return between symptom episodes. |

---

*Document version 1.0 — Generated from SymptomScope AI codebase analysis (July 2026)*
