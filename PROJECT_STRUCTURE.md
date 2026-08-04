# PROJECT STRUCTURE

## Root Directory
```
SymptomScope AI/
├── backend/                    # FastAPI backend
├── frontend/                   # Next.js 15 frontend
├── scripts/                    # Utility scripts
├── .github/                    # GitHub Actions workflows
├── .opencode/                  # OpenCode configuration
├── .vscode/                    # VS Code settings
├── boot.sh                     # Linux/macOS startup script
├── start.bat                   # Windows startup script
├── CLEANUP_REPORT.md           # Cleanup documentation
├── FINAL_VERIFICATION.md       # This verification report
├── PROJECT_STRUCTURE.md        # This file
├── RECOVERY_PLAN.md            # Recovery Plan feature docs
├── STARTUP_GUIDE.md            # Startup instructions
├── README.md                   # Project overview
└── package.json                # Root package (if any)
```

## Backend Structure
```
backend/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── analytics.py
│       ├── chat.py
│       ├── doctors.py
│       ├── export.py
│       ├── hospitals.py
│       ├── predict.py
│       ├── recovery.py         # NEW: Recovery Plan endpoints
│       ├── reminders.py
│       ├── reports.py
│       ├── risk_score.py
│       └── symptoms.py
├── auth/
│   ├── __init__.py
│   └── dependency.py           # Clerk JWT validation
├── bin/
│   ├── audit.py
│   └── startup_check.py
├── ml/
│   ├── data/
│   │   ├── download_kaggle.py
│   │   └── kaggle_pipeline.py
│   ├── preprocessing/
│   │   └── preprocess.py
│   ├── rag/
│   │   └── init_knowledge_base.py
│   ├── training/
│   │   └── train_models.py
│   ├── models/                 # Trained .pkl files (gitignored)
│   │   ├── decision_tree_v1.pkl
│   │   ├── random_forest_v1.pkl
│   │   └── naive_bayes_v1.pkl
│   └── prompts/                # LLM prompt templates
│       ├── chat.txt
│       ├── explain_prediction.txt
│       ├── follow_up_questions.txt
│       └── medical_qa.txt
├── repositories/
│   ├── __init__.py
│   ├── chat_repository.py
│   ├── doctor_repository.py
│   ├── hospital_repository.py
│   ├── prediction_repository.py
│   ├── recovery_repository.py  # NEW: Recovery plan storage
│   ├── reminder_repository.py
│   └── risk_score_repository.py
├── schemas/
│   ├── __init__.py
│   ├── analytics_schema.py
│   ├── chat_schema.py
│   ├── doctor_schema.py
│   ├── hospital_schema.py
│   ├── prediction_schema.py
│   ├── recovery_schema.py      # NEW: Recovery plan models
│   ├── reminder_schema.py
│   └── risk_score_schema.py
├── services/
│   ├── __init__.py
│   ├── analytics_service.py
│   ├── chat_service.py
│   ├── doctor_service.py
│   ├── emergency_service.py
│   ├── explainability_service.py
│   ├── feature_engineering.py
│   ├── hospital_service.py
│   ├── llm_service.py          # UPDATED: Centralized with fallbacks
│   ├── model_registry.py
│   ├── prediction_service.py
│   ├── precaution_service.py
│   ├── rag_service.py
│   ├── reminder_service.py
│   ├── risk_score_service.py
│   ├── report_export_service.py
│   ├── report_service.py
│   └── severity_service.py
├── tests/
│   ├── conftest.py
│   ├── test_analytics_service.py
│   ├── test_doctor_service.py
│   ├── test_emergency_service.py
│   ├── test_feature_engineering.py
│   ├── test_hospital_service.py
│   ├── test_precaution_service.py
│   ├── test_prediction_repository.py
│   ├── test_prediction_service.py
│   ├── test_report_service.py
│   ├── test_risk_score_service.py
│   ├── test_search_service.py
│   ├── test_severity_service.py
│   └── test_symptom_search_service.py
├── utils/
│   ├── __init__.py
│   ├── database.py             # MongoDB connection (Motor)
│   ├── env_check.py
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── rate_limit.py
│   ├── request_logger.py
│   └── settings.py             # Pydantic Settings
├── .env                        # Local env (gitignored)
├── .env.example                # Template
├── main.py                     # FastAPI app entry
├── requirements.txt            # Python dependencies
├── pytest.ini
├── conftest.py
└── AUDIT_REPORT.md
```

## Frontend Structure
```
frontend/
├── public/                     # Static assets
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── auth/
│   │   │       ├── sign-in/[[...sign-in]]/page.tsx
│   │   │       └── sign-up/[[...sign-up]]/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── history/
│   │   │   │   └── page.tsx
│   │   │   ├── recovery-plan/  # NEW: Recovery Plan page
│   │   │   │   └── page.tsx
│   │   │   ├── reminders/
│   │   │   │   └── page.tsx
│   │   │   ├── reports/
│   │   │   │   └── page.tsx
│   │   │   ├── results/
│   │   │   │   └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   ├── symptom-checker/
│   │   │   │   └── page.tsx
│   │   │   ├── dashboard-layout-client.tsx
│   │   │   └── layout.tsx
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── home-content.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── providers.tsx       # UPDATED: Removed PostHog/Sentry
│   ├── components/
│   │   ├── features/
│   │   │   ├── chat/
│   │   │   │   ├── chat-input.tsx
│   │   │   │   ├── chat-message.tsx
│   │   │   │   └── chat-widget.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── disease-charts-row.tsx
│   │   │   │   ├── health-insights.tsx
│   │   │   │   ├── health-summary-banner.tsx
│   │   │   │   ├── recommendation-history.tsx
│   │   │   │   ├── recurring-conditions.tsx
│   │   │   │   ├── symptom-progress-trends.tsx
│   │   │   │   ├── symptom-timeline.tsx
│   │   │   │   ├── symptoms-confidence-row.tsx
│   │   │   │   ├── summary-cards.tsx
│   │   │   │   └── trend-charts-row.tsx
│   │   │   ├── history/
│   │   │   │   ├── health-summary-strip.tsx
│   │   │   │   ├── history-timeline.tsx
│   │   │   │   └── summary-charts.tsx
│   │   │   ├── reminders/
│   │   │   │   ├── reminder-card.tsx
│   │   │   │   ├── reminder-dashboard-card.tsx
│   │   │   │   ├── reminder-form.tsx
│   │   │   │   ├── reminder-list.tsx
│   │   │   │   └── reminder-status-badge.tsx
│   │   │   ├── reports/
│   │   │   │   ├── report-charts.tsx
│   │   │   │   ├── report-export.tsx
│   │   │   │   ├── report-insights.tsx
│   │   │   │   ├── report-prediction-history.tsx
│   │   │   │   └── report-summary.tsx
│   │   │   ├── __tests__/      # Component tests
│   │   │   ├── analyzing-step.tsx
│   │   │   ├── details-step.tsx
│   │   │   ├── doctor-recommendation-card.tsx
│   │   │   ├── dashboard-analytics-content.tsx
│   │   │   ├── emergency-action-panel.tsx
│   │   │   ├── features-section.tsx
│   │   │   ├── footer.tsx
│   │   │   ├── header.tsx
│   │   │   ├── hero-section.tsx
│   │   │   ├── how-it-works-section.tsx
│   │   │   ├── keyboard-shortcuts.tsx
│   │   │   ├── prediction-results.tsx
│   │   │   ├── risk-score/     # Risk score components
│   │   │   ├── step-indicator.tsx
│   │   │   ├── symptom-selection-step.tsx
│   │   │   └── theme-init.tsx
│   │   ├── layouts/
│   │   │   ├── dashboard-header.tsx
│   │   │   └── dashboard-sidebar.tsx  # UPDATED: Added Recovery Plan link
│   │   ├── shared/
│   │   │   ├── custom-tooltip.tsx
│   │   │   ├── dashboard-types.ts
│   │   │   ├── severity-badge.tsx
│   │   │   └── trend-icon.tsx
│   │   └── ui/                 # shadcn/ui components
│   │       ├── alert.tsx
│   │       ├── avatar.tsx
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── dropdown-menu.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── scroll-area.tsx
│   │       ├── select.tsx
│   │       ├── separator.tsx
│   │       ├── skeleton.tsx
│   │       ├── sonner.tsx
│   │       ├── switch.tsx
│   │       ├── tabs.tsx
│   │       ├── textarea.tsx
│   │       └── __tests__/
│   ├── lib/
│   │   ├── api/
│   │   │   ├── chat.ts
│   │   │   ├── predictions.ts
│   │   │   ├── recovery.ts       # NEW: Recovery API client
│   │   │   ├── reminders.ts
│   │   │   ├── risk-score.ts
│   │   │   └── __tests__/
│   │   ├── stores/
│   │   │   ├── chat-store.ts
│   │   │   ├── dashboard-store.ts
│   │   │   ├── reminder-store.ts
│   │   │   ├── risk-score-store.ts
│   │   │   ├── theme-store.ts
│   │   │   └── __tests__/
│   │   ├── utils.ts
│   │   ├── clerk-provider.tsx
│   │   ├── focus-trap.ts
│   │   ├── posthog-provider.tsx  # REMOVED
│   │   ├── query-provider.tsx
│   │   ├── sentry-provider.tsx   # REMOVED
│   │   └── validations/
│   │       ├── symptom-form.ts
│   │       └── __tests__/
│   ├── middleware.ts             # Clerk auth protection
│   └── test/
│       └── setup.ts
├── .env.example                  # UPDATED: Removed PostHog/Sentry/Cloudinary
├── .env.local                    # Local env (gitignored)
├── .gitignore
├── .dockerignore                 # REMOVED
├── Dockerfile                    # REMOVED
├── AGENTS.md
├── README.md
├── components.json
├── eslint.config.mjs
├── next.config.ts                # UPDATED: CSP without PostHog/Sentry
├── next-env.d.ts
├── package.json                  # UPDATED: Removed PostHog/Sentry deps
├── package-lock.json
├── postcss.config.mjs
├── tsconfig.json
└── vitest.config.ts
```

## Key Files Modified for Recovery Plan

### Backend
| File | Change |
|------|--------|
| `api/v1/recovery.py` | NEW: 4 REST endpoints |
| `api/v1/predict.py` | Added `/predictions/latest` and `/predictions/history` |
| `schemas/recovery_schema.py` | NEW: Pydantic models |
| `repositories/recovery_repository.py` | NEW: MongoDB operations |
| `main.py` | Registered recovery router |
| `services/llm_service.py` | UPDATED: Fallback chain + retry/timeout |

### Frontend
| File | Change |
|------|--------|
| `app/(dashboard)/recovery-plan/page.tsx` | NEW: Full page component |
| `lib/api/recovery.ts` | NEW: API client functions |
| `components/layouts/dashboard-sidebar.tsx` | Added Recovery Plan link |
| `app/providers.tsx` | Removed PostHog/Sentry providers |

---

## Dependencies

### Backend (requirements.txt)
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
reportlab>=4.3.1
pydantic>=2.10.0
pydantic-settings>=2.7.0
motor>=3.6.0
joblib>=1.4.2
python-multipart>=0.0.20
pytest>=8.3.0
pytest-asyncio>=0.25.0
httpx>=0.28.0
python-dotenv>=1.0.1
pyjwt>=2.10.0
cryptography>=44.0.0
slowapi>=0.1.9
redis>=5.2.0
scikit-learn>=1.6.0
pandas>=2.2.0
numpy>=1.26.0
shap>=0.46.0
langchain>=0.3.0
langchain-groq>=0.1.0
langchain-core>=0.3.0
langchain-chroma>=0.2.0
langchain-text-splitters>=0.3.0
google-generativeai>=0.8.0    # NEW: Direct SDK fallback
tenacity>=8.2.0                # NEW: Retry logic
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "@base-ui/react": "^1.5.0",
    "@clerk/nextjs": "^7.4.3",
    "@clerk/themes": "^2.4.57",
    "@hookform/resolvers": "^5.4.0",
    "@tanstack/react-query": "^5.101.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "framer-motion": "^12.40.0",
    "lucide-react": "^1.17.0",
    "next": "^15.4.10",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-hook-form": "^7.78.0",
    "recharts": "^3.8.1",
    "sonner": "^2.0.7",
    "tailwind-merge": "^3.6.0",
    "tw-animate-css": "^1.4.0",
    "zod": "^4.4.3",
    "zustand": "^5.0.14"
  }
}
```

---

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### Backend (.env)
```
MONGODB_URI=mongodb://localhost:27017/symptomscope
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CLERK_ISSUER=https://your-clerk.clerk.accounts.dev
CLERK_JWKS_URL=https://your-clerk.clerk.accounts.dev/.well-known/jwks.json
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1024
GROQ_API_KEY=your_groq_key          # NEW: Optional fallback
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1024
```

---

## Data Flow: Recovery Plan

```
User completes symptom checker
         ↓
Prediction stored in MongoDB (predictions collection)
         ↓
User clicks "Recovery Plan" in sidebar
         ↓
Frontend calls GET /api/v1/predictions/latest
         ↓
Backend returns latest prediction for user
         ↓
Frontend calls POST /api/v1/recovery-plan/generate { prediction_id }
         ↓
Backend fetches prediction + builds LLM context
         ↓
LLMService.invoke() with fallback chain
         ↓
Structured JSON plan parsed & stored (recovery_plans collection)
         ↓
Frontend displays plan in tabbed UI
         ↓
User can Regenerate → POST /api/v1/recovery-plan/regenerate { plan_id }
```