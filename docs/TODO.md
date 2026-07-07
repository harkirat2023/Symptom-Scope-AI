# Symptom Scope AI — Project Todo List

## Legend
- Each task is **atomic** and ordered sequentially (no overlapping dependencies).
- Complete each task fully before moving to the next.
- A task is done only when all "Definition of Done" criteria are met (see AGENTS.md).

---

| # | Task | Description |
|---|------|-------------|
| 1 | **Initialize Next.js 16 project** | Scaffold with TypeScript, Tailwind CSS v4, shadcn/ui, Framer Motion |
| 2 | **Set up design system foundation** | Configure colors (#2563EB, #14B8A6, #0F172A, etc.), Inter typography, spacing, card/button/input base styles |
| 3 | **Configure Zustand + TanStack Query** | Set up Zustand stores (auth, symptom selection, dashboard prefs) and TanStack Query for API caching |
| 4 | **Integrate Clerk authentication** | Add Clerk provider, login/signup pages (Email, Google, OTP), protected routes, session middleware |
| 5 | **Build Landing / Home page** | Hero section with headline, subheading, CTA buttons, 3D medical illustration placeholder, Learn More section |
| 6 | **Scaffold FastAPI backend** | Initialize FastAPI project with Pydantic models, Uvicorn, Python 3.13, project structure |
| 7 | **Set up MongoDB Atlas connection & collections** | Define collections: `users`, `predictions`, `reports`, `symptom_logs`, `doctors`, `hospitals`, `alerts` |
| 8 | **Train ML models (Decision Tree + Random Forest)** | Build training pipeline with Scikit-Learn on symptom-disease dataset, serialize with Joblib |
| 9 | **Build feature engineering pipeline** | Symptom encoding, missing value handling, normalization, transformation endpoint |
| 10 | **Implement disease prediction API** | Load trained models, run inference, return top disease probabilities |
| 11 | **Implement confidence score calculation** | Compute confidence = highest probability × 100, return with alternatives |
| 12 | **Integrate SHAP explainability** | Feature importance ranking, top contributing symptoms per prediction |
| 13 | **Build severity classification engine** | Map predicted disease to Mild/Moderate/Severe categories |
| 14 | **Build precaution recommendation engine** | Disease-to-precaution mapping, return actionable health guidance |
| 15 | **Build doctor recommendation engine (Phase 1)** | Static curated doctor database with specialty mapping by disease/location |
| 16 | **Build emergency detection engine** | Trigger rules: Severity=Severe OR (Confidence>90% for critical diseases) |
| 17 | **Build prediction storage endpoint** | Save prediction records to MongoDB with userId, symptoms, prediction, confidence, severity, timestamp |
| 18 | **Build Symptom Checker UI** | Multi-step form: Step 1 (searchable symptom input + auto-suggest), Step 2 (age/gender/duration/pain), Step 3 (loading animation), Step 4 (results) |
| 19 | **Connect frontend to prediction API** | Wire symptom form → API call → display results (disease, confidence, severity, alternatives) |
| 20 | **Build Results page** | Prediction card with disease name, confidence score, severity badge, top contributing symptoms, precautions, doctor recommendations |
| 21 | **Build Dashboard Analytics page** | Widgets: latest prediction, monthly health score, symptom frequency, disease trends, severity trends — using Recharts |
| 22 | **Build Prediction History page** | Paginated list of past predictions with search/filter |
| 23 | **Implement Report Generation** | Export PDF and CSV with symptom history, predictions, confidence scores, severity trends, precautions |
| 24 | **Build Emergency Alert UI** | Full-width red banner with ambulance call, nearby hospitals map, teleconsultation CTA |
| 25 | **Implement Dark Mode** | Dark theme colors (#020617 bg, #0F172A cards, #F8FAFC text), toggle persistence |
| 26 | **Add Framer Motion animations** | Fade-in, slide-up, scale hover, progress animation, microinteractions (150-300ms) |
| 27 | **Integrate Cloudinary file storage** | Upload/retrieve medical reports and exported PDFs |
| 28 | **Set up Novu notifications** | Emergency alerts, severe disease notifications, report generation updates |
| 29 | **Set up Sentry monitoring** | ✅ Done — Backend `sentry-sdk` integrated in `utils/monitoring.py`; frontend `@sentry/nextjs` in `lib/sentry-provider.tsx` |
| 30 | **Set up PostHog analytics** | ✅ Done — `posthog-js` integrated in `lib/posthog-provider.tsx` with pageview tracking |
| 31 | **Deploy frontend to Vercel** | ✅ Done — Deployment config in `frontend/Dockerfile`, CI/CD in `.github/workflows/deploy.yml` |
| 32 | **Deploy backend to Railway** | ✅ Done — Deployment config in `backend/Dockerfile`, `railway.json`, CI/CD in `.github/workflows/deploy.yml` |
| 33 | **Set up GitHub Actions CI/CD** | ✅ Done — Three workflows: `backend-ci.yml`, `frontend-ci.yml`, `deploy.yml` |
| 34 | **Set up structured logging** | ✅ Done — JSON/formatted logging in `utils/logging_config.py`, request logging middleware |
| 35 | **Environment management** | ✅ Done — Pydantic Settings in `utils/settings.py`, enhanced `.env.example` files, `utils/env_check.py` |
| 36 | **Deployment scripts** | ✅ Done — `docker-compose.yml`, `scripts/deploy.sh`, `scripts/setup-local.sh`, `railway.json` |
| 37 | **Documentation** | ✅ Done — `SETUP.md` with from-scratch setup guide for new engineers |
