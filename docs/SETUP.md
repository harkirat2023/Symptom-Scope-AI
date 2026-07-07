# SymptomScope AI — Setup Guide

This guide walks you through setting up and running the entire SymptomScope AI platform from scratch.

---

## Prerequisites

| Tool      | Version | Purpose                    |
|-----------|---------|----------------------------|
| Python    | 3.13+   | Backend runtime            |
| Node.js   | 22+     | Frontend runtime           |
| MongoDB   | 7+      | Database (local or Atlas)  |
| Docker    | 24+     | Containerized development  |

---

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd symptom-scope-ai

# 2. Set up environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Edit the environment files with your credentials (see below)

# 4. Start everything
docker-compose up --build
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Manual Setup

### 1. Clone and Prepare

```bash
git clone <repo-url>
cd symptom-scope-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
# .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm ci

# Configure environment
cp .env.example .env.local
# Edit .env.local with your settings
```

### 4. Start MongoDB

```bash
# Option A: Local install
mongod

# Option B: Docker
docker run -d -p 27017:27017 mongo:7
```

### 5. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Frontend

```bash
cd frontend
npm run dev
```

---

## Environment Configuration

### Backend (`backend/.env`)

```env
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017/symptomscope

# Allowed CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000

# Clerk auth (at least one required)
CLERK_JWKS_URL=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json
# CLERK_ISSUER=https://your-clerk-instance.clerk.accounts.dev

# Sentry error tracking (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Frontend (`frontend/.env.local`)

```env
# Clerk credentials (from https://dashboard.clerk.com)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# PostHog analytics (optional)
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

# Sentry error tracking (optional)
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Import repository in Vercel
3. Set environment variables in Vercel project settings
4. Deploy (automatic on main branch pushes)

Or using CLI:

```bash
cd frontend
vercel --prod
```

### Backend (Railway)

1. Push code to GitHub
2. Create new Railway project from repository
3. Set `backend/` as root directory
4. Add environment variables in Railway dashboard
5. Deploy

Or using CLI:

```bash
railway up --service symptomscope-api
```

### CI/CD Pipeline

The `.github/workflows/` directory contains three pipelines:

| Workflow         | Trigger                     | Actions                              |
|------------------|-----------------------------|--------------------------------------|
| `backend-ci.yml` | Push to main/develop (backend/) | Lint (ruff), test (pytest), build |
| `frontend-ci.yml`| Push to main/develop (frontend/)| Lint (eslint), test (vitest), build |
| `deploy.yml`     | Push to main                | Deploy frontend to Vercel + backend to Railway |

---

## Project Structure

```
symptom-scope-ai/
├── backend/                  # FastAPI backend
│   ├── api/                  # Route handlers
│   ├── services/             # Business logic
│   ├── repositories/         # Data access layer
│   ├── schemas/              # Pydantic models
│   ├── models/               # ML models
│   ├── utils/                # Utilities (DB, auth, logging, etc.)
│   ├── main.py               # Application entry point
│   ├── Dockerfile            # Container image
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/              # Pages and layouts
│   │   ├── components/       # UI and feature components
│   │   └── lib/              # Providers, stores, utilities
│   ├── public/               # Static assets
│   ├── Dockerfile            # Container image
│   └── package.json          # Node.js dependencies
├── .github/workflows/        # CI/CD pipelines
├── scripts/                  # Deployment and setup scripts
├── docs/                     # Documentation
├── docker-compose.yml        # Local development orchestration
├── railway.json              # Railway deployment config
└── SETUP.md                  # This file
```

---

## Monitoring & Analytics

| Service  | Purpose           | Configuration                     |
|----------|-------------------|-----------------------------------|
| Sentry   | Error tracking    | `SENTRY_DSN` in both .env files   |
| PostHog  | Product analytics | `NEXT_PUBLIC_POSTHOG_*` in frontend |
| Logging  | Structured logs   | `LOG_LEVEL`, `LOG_FORMAT` in backend |

---

## Useful Commands

```bash
# Run backend tests
cd backend && pytest -v

# Run frontend tests
cd frontend && npm test

# Run all tests with coverage
cd frontend && npm run test:coverage

# Lint backend
cd backend && ruff check .

# Lint frontend
cd frontend && npm run lint

# Build frontend
cd frontend && npm run build
```

---

## Troubleshooting

**MongoDB connection refused**
- Ensure MongoDB is running: `mongod` or `docker ps`
- Check `MONGODB_URI` in `backend/.env`

**CORS errors**
- Ensure `CORS_ORIGINS` in `backend/.env` includes your frontend URL

**Clerk auth not working**
- Verify both `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` are set
- Check that the JWKS URL or Issuer is configured in the backend

**Rate limiting issues**
- Rate limits are configured via `slowapi` — check `utils/rate_limit.py`
