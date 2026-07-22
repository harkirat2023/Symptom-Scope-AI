# SymptomScope AI — Operational State Document

> **Generated:** 2026-07-22
> **Current Status:** All backend modules operational | Frontend verified | 16/16 API endpoints passing

---

## 1. Tech Stack

### Backend
| Category | Technology | Version |
|---|---|---|
| **Runtime** | Python | 3.13-slim |
| **Framework** | FastAPI | 0.115+ |
| **Server** | Uvicorn | 0.34+ |
| **Database Driver** | Motor (async MongoDB) | 3.6+ |
| **Validation** | Pydantic | 2.10+ |
| **Settings** | Pydantic-Settings | 2.7+ |
| **ML** | scikit-learn, joblib | latest |
| **Explainability** | SHAP | latest |
| **Auth** | PyJWT + Clerk JWKS | 2.10+ |
| **Rate Limiting** | slowapi | 0.1.9 |
| **PDF Export** | ReportLab | 4.3+ |
| **CSV Export** | Python csv (stdlib) | — |
| **HTTP Client** | httpx | 0.28+ |
| **Testing** | pytest, pytest-asyncio | 8.3+ / 0.25+ |
| **Data** | pandas, numpy | latest |

### Frontend
| Category | Technology | Version |
|---|---|---|
| **Framework** | Next.js | 15.5+ |
| **Language** | TypeScript | ~5.x |
| **Styling** | Tailwind CSS | v4 |
| **UI Library** | shadcn/ui + @base-ui/react | latest |
| **Icons** | lucide-react | latest |
| **State** | Zustand | v5 |
| **Auth** | Clerk (@clerk/nextjs) | v7 |
| **Data Fetching** | TanStack Query | v5 |
| **Form** | React Hook Form + Zod | latest |
| **Charts** | recharts | latest |
| **Animation** | framer-motion | latest |
| **Toast** | sonner | latest |
| **Error Tracking** | @sentry/nextjs | v9 |
| **Analytics** | PostHog (posthog-js) | v1 |
| **Testing** | Vitest + @testing-library/react | latest |

---

## 2. Active Ports

| Service | Port | Status |
|---|---|---|
| MongoDB | 27017 | Required |
| Backend (FastAPI) | 8080 | Running |
| Frontend (Next.js) | 3000 | Running |
| API Docs (Swagger) | 8080/docs | Available |

---

## 3. Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend  │────▶│   Backend    │────▶│   MongoDB    │
│  Next.js 15 │     │  FastAPI     │     │   (Motor)    │
│  :3000      │     │  :8080       │     │  :27017      │
└─────────────┘     └──────────────┘     └──────────────┘
                          │
                          ├── ML Models (joblib/.pkl)
                          ├── SHAP Explainer
                          ├── ReportLab (PDF)
                          └── SMTP (Email, optional)
```

### Directory Structure
```
backend/
├── api/v1/              # 10 route modules
├── auth/                # Clerk JWT verification
├── services/            # 18 business logic services
├── repositories/        # 4 MongoDB data access
├── schemas/             # 9 Pydantic models
├── utils/               # 7 utility modules
├── ml/                  # ML models + training
├── tests/               # 13 test files
├── main.py              # Entry point
├── Dockerfile           # Container definition
├── requirements.txt     # Python deps
└── pytest.ini

frontend/
├── src/app/             # 11 pages (App Router)
├── src/components/      # ~60 components
├── src/lib/             # API, stores, validation
├── src/middleware.ts     # Clerk route protection
├── Dockerfile           # Container definition
├── next.config.ts       # Next.js config
└── package.json

Root:
├── docker-compose.yml   # Multi-service orchestration
├── start-SymptomScope.bat  # One-click launcher
└── scripts/             # Deploy/setup helpers
```

---

## 4. API Routes (24 total)

### 4.1 Symptom Prediction
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/predict` | ✅ | 10/min | Predict disease from symptoms |

**Pipeline:**
1. `SymptomInput` validated (symptoms, age, gender, existing_conditions, duration, pain_level)
2. `FeatureEngineeringService.encode_symptoms()` → 31 binary feature vector
3. `PredictionService.predict()` → DecisionTree + RandomForest ensemble
4. Top 3 diseases by probability, confidence = highest probability
5. `SeverityService.classify()` → base + escalation check
6. `PrecautionService.get_precautions()` → disease-specific or fallback
7. `EmergencyService.detect()` → 4-factor emergency check
8. `DoctorService` → 3 specialist recommendations
9. `ExplainabilityService.build_contributing_symptoms()` → SHAP top-5
10. `PredictionRepository.create()` → saved to MongoDB
11. `RiskScoreService.compute_and_save()` → 9-factor score
12. Analytics cache invalidated

### 4.2 Symptoms
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/symptoms/search` | ✅ | 30/min | Search by query/category |
| `GET` | `/api/v1/symptoms/categories` | ✅ | 30/min | List categories |
| `GET` | `/api/v1/symptoms` | ✅ | 30/min | List all 31 symptoms |

### 4.3 Doctors
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/doctors` | ✅ | 30/min | Search/filter 8 doctors |
| `GET` | `/api/v1/doctors/specialties` | ✅ | 30/min | List 7 specialties |
| `GET` | `/api/v1/doctors/locations` | ✅ | 30/min | List locations |

### 4.4 Hospitals
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/hospitals` | ✅ | 30/min | Search/filter 8 hospitals |
| `GET` | `/api/v1/hospitals/locations` | ✅ | 30/min | List locations |

### 4.5 Reports
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/reports/{user_id}` | ✅ | 10/min | Health report with severity dist |

### 4.6 Export
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/export/csv/{user_id}` | ✅ | 10/min | CSV export |
| `GET` | `/api/v1/export/pdf/{user_id}` | ✅ | 10/min | PDF export via ReportLab |

### 4.7 Analytics
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/analytics/{user_id}` | ✅ | 10/min | Full analytics suite |

### 4.8 Chat
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/chat/session` | ✅ | 10/min | Create session |
| `GET` | `/api/v1/chat/sessions` | ✅ | 10/min | List sessions |
| `POST` | `/api/v1/chat/message` | ✅ | 5/min | Send message |
| `GET` | `/api/v1/chat/messages/{session_id}` | ✅ | 10/min | Get messages |

### 4.9 Reminders
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/reminders` | ✅ | 10/min | Create |
| `GET` | `/api/v1/reminders` | ✅ | 10/min | List (status filter) |
| `PUT` | `/api/v1/reminders/{id}` | ✅ | 10/min | Update |
| `DELETE` | `/api/v1/reminders/{id}` | ✅ | 10/min | Delete |
| `POST` | `/api/v1/reminders/{id}/log` | ✅ | 10/min | Log status |
| `GET` | `/api/v1/reminders/upcoming` | ✅ | 10/min | Next upcoming |

### 4.10 Risk Score
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/risk-score` | ✅ | 10/min | Current score + breakdown |
| `GET` | `/api/v1/risk-score/history` | ✅ | 10/min | Score history |
| `GET` | `/api/v1/risk-score/tips` | ✅ | 10/min | Reduction tips |
| `PUT` | `/api/v1/risk-score/profile` | ✅ | 10/min | Update profile |
| `GET` | `/api/v1/risk-score/profile` | ✅ | 10/min | Get profile |

### 4.11 Health Check
| Method | Route | Auth | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/health` | ❌ | None | `{"status":"healthy","version":"1.0.0"}` |

---

## 5. Database Collections (7)

| Collection | Key Indexes |
|---|---|
| `predictions` | `userId`, `userId+timestamp` (compound desc), `timestamp` |
| `chat_sessions` | `userId`, `userId+lastActivityAt` (compound desc) |
| `chat_messages` | `sessionId`, `sessionId+createdAt` (compound) |
| `medicine_reminders` | `userId`, `userId+status`, `nextDueAt` |
| `reminder_logs` | `reminderId`, `reminderId+timestamp` (compound desc) |
| `health_risk_scores` | `userId`, `userId+timestamp` (compound desc) |
| `user_health_profiles` | `userId` (unique) |

---

## 6. ML Models

| File | Algorithm | Purpose |
|---|---|---|
| `decision_tree_v1.pkl` | DecisionTree (max_depth=10) | Fast interpretable predictions |
| `random_forest_v1.pkl` | RandomForest (150 est, max_depth=12) | Higher accuracy |
| `label_encoder_v1.pkl` | LabelEncoder | 15 disease classes |
| `symptom_columns_v1.pkl` | list[str] | 31 symptom features |

**15 Diseases:** Common Cold, Allergy, Mild Food Poisoning, Influenza, Bronchitis, Gastroenteritis, Migraine, Pneumonia, Heart Attack, Stroke, Severe Respiratory Distress, Malaria, Dengue, COVID-19, Epilepsy

---

## 7. Known Issues

### Critical
1. ML models trained on synthetic data (not clinically validated)
2. Doctor/Hospital data hardcoded (8 each, Punjab only)
3. LLM Chat requires external service; falls back if not configured
4. Email service silently skips if SMTP not configured

### Moderate
5. Analytics cache is in-memory (60s TTL, not distributed)
6. JWKS cache is in-memory (3600s TTL)
7. PredictionRepository capped at 100 records
8. No user registration on backend (trusts any valid Clerk JWT)
9. `/health` outside `/api/v1` prefix

### Minor
10. No pagination on list endpoints
11. Symptom data is static (31 hardcoded)
12. No cursor-based pagination
13. Chart colors mix CSS vars and hardcoded hex

---

## 8. Frontend Routes

| Route | Auth | Description |
|---|---|---|
| `/` | No | Landing/hero page |
| `/auth/sign-in` | No | Clerk sign-in |
| `/auth/sign-up` | No | Clerk sign-up |
| `/dashboard` | Yes | Analytics dashboard |
| `/history` | Yes | Prediction history |
| `/reports` | Yes | Reports + export |
| `/reminders` | Yes | Medicine reminders |
| `/settings` | Yes | Profile + preferences |
| `/symptom-checker` | Yes | Multi-step symptom checker |
| `/results` | Optional | Standalone results |

---

## 9. Environment Variables

### Backend (`backend/.env`)
| Variable | Required | Default |
|---|---|---|
| `MONGODB_URI` | Yes | `mongodb://localhost:27017/symptomscope` |
| `CORS_ORIGINS` | Yes | `http://localhost:3000,...` |
| `CLERK_JWKS_URL` | One of | — |
| `CLERK_ISSUER` | One of | — |
| `LOG_LEVEL` | No | `INFO` |
| `REDIS_URL` | No | — |
| `LLM_API_URL` | No | — |
| `LLM_API_KEY` | No | — |
| `SMTP_*` | No | — |

### Frontend (`frontend/.env.local`)
| Variable | Required | Default |
|---|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | — |
| `CLERK_SECRET_KEY` | Yes | — |
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8080` |
| `NEXT_PUBLIC_SENTRY_DSN` | No | — |
| `NEXT_PUBLIC_POSTHOG_KEY` | No | — |
| `NEXT_PUBLIC_POSTHOG_HOST` | No | `https://us.i.posthog.com` |

---

## 10. Infrastructure

| File | Purpose |
|---|---|
| `backend/Dockerfile` | Backend container |
| `frontend/Dockerfile` | Frontend container |
| `docker-compose.yml` | Orchestrates MongoDB + Backend + Frontend |
| `start-SymptomScope.bat` | One-click launcher for local dev |
| `scripts/deploy.sh` | Deploy to Vercel/Railway |
| `scripts/setup-local.sh` | Local dev environment setup |
