# SymptomScope AI

AI-powered healthcare intelligence platform — symptom analysis, disease prediction, and health recommendations.

## Quick Start

### Docker (Recommended)

```bash
# Start all services with one command
docker compose up --build
```

Or use the startup script (auto-opens browser):
- **Windows:** `start-SymptomScope.bat`
- **Linux/macOS:** `bash start-SymptomScope.sh`

### Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js web application |
| Backend API | http://localhost:8080 | FastAPI REST API |
| API Docs | http://localhost:8080/docs | Interactive Swagger docs |

### Local Development (No Docker)

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # Edit with your keys
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Frontend
cd frontend
npm install
cp .env.example .env.local   # Edit with your keys
npm run dev

# Or use the unified script
bash boot.sh
```

## Features

- **Multi-Step Symptom Checker** — Select symptoms, add details, get analysis
- **Disease Prediction** — Ensemble ML (Decision Tree + Random Forest + Naive Bayes)
- **SHAP Explainability** — Understand which symptoms drive predictions
- **Severity Classification** — Mild / Moderate / Severe with escalation logic
- **Emergency Detection** — Automatic flagging of critical conditions
- **Doctor & Hospital Recommendations** — Specialty-matched provider suggestions
- **Precaution Guidance** — Disease-specific priority-ordered list
- **AI Medical Report Explainer** — LLM-powered explanation of results
- **AI Follow-up Symptom Assistant** — Smart follow-up question generation
- **Medical Knowledge Assistant (RAG)** — ChromaDB + Gemini grounded Q&A
- **Health Dashboard** — Analytics, charts, trends, risk score
- **PDF & CSV Reports** — Downloadable health reports
- **Medication Reminders** — Track and log medications
- **Dark/Light Theme** — Persistent theme selection

## Architecture

```
Frontend (Next.js 15 + Clerk Auth + Zustand + TanStack Query)
    │ HTTP (Bearer JWT)
Backend (FastAPI + Motor + MongoDB)
    ├── ML Pipeline: DT + RF + NB ensemble + SHAP
    ├── AI Pipeline: LangChain + Gemini 2.5 Flash + ChromaDB RAG
    └── Services: Prediction, Severity, Emergency, Doctors, Hospitals, Chat, etc.
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Zustand, TanStack Query, Recharts |
| **Backend** | Python 3.13+, FastAPI, Motor, Pydantic, scikit-learn, SHAP |
| **AI/ML** | LangChain, Gemini 1.5 Flash, ChromaDB, Google GenAI Embeddings |
| **Database** | MongoDB 7+ (Atlas compatible) |
| **Auth** | Clerk (JWT + JWKS) |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions |

## Documentation

- [Architecture](docs/LATEST_DOCS/ARCHITECTURE.md)
- [API Reference](docs/LATEST_DOCS/API_REFERENCE.md)
- [Database Schema](docs/LATEST_DOCS/DATABASE_SCHEMA.md)
- [ML Pipeline](docs/LATEST_DOCS/ML_PIPELINE.md)
- [AI Pipeline](docs/LATEST_DOCS/AI_PIPELINE.md)
- [Environment Setup](docs/LATEST_DOCS/ENVIRONMENT.md)
- [Deployment Guide](docs/LATEST_DOCS/DEPLOYMENT.md)
- [User Workflows](docs/LATEST_DOCS/USER_WORKFLOWS.md)

## License

Educational project — not for clinical use. See medical disclaimer in application.
