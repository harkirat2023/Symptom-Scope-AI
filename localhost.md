# Localhost Setup (Run Full Project Locally)

This project has a **React/Next.js frontend** and a **FastAPI backend** plus **MongoDB**.

## 0) Prerequisites
- **Docker Desktop** (recommended, uses `docker-compose.yml`)
- Ports:
  - Frontend: `3000`
  - Backend: `8000`
  - MongoDB: `27017`

## 1) Run everything with Docker Compose (recommended)
From the project root:

```bash
cd "d:/1. PLACEMENT/1A. PROJECTS/Symptom Scope AI"
docker-compose up --build
```

When containers are healthy:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/docs
- Backend health: http://localhost:8080/health

Stop it with:
```bash
docker-compose down
```

## 2) Run backend only (Python / FastAPI)
### 2.1 Create a virtual environment
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
```

### 2.2 Install dependencies
```bash
pip install -r requirements.txt
```

### 2.3 Configure environment variables
- Copy env template (if present) or create your own:
  - `backend/.env`

At minimum you typically need (names may vary—check `backend/.env`):
- `MONGODB_URI`
- `CORS_ORIGINS`

### 2.4 Start the API
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Open:
- API docs: http://localhost:8080/docs

## 3) Run frontend only (Next.js)
### 3.1 Install dependencies
```bash
cd frontend
npm install
```

### 3.2 Configure environment variables
- Create `frontend/.env.local` (already referenced by `docker-compose.yml`)

### 3.3 Start the dev server
```bash
npm run dev
```

Open:
- http://localhost:3000

## 4) Train / ML artifacts (if applicable)
The backend loads ML models at runtime (see `backend/main.py` and ML modules under `backend/ml/`). If training is part of your workflow, check:
- `backend/ml/training/train_models.py`

Run training (if needed):
```bash
python backend/ml/training/train_models.py
```

## Notes / Troubleshooting
- **CORS errors**: ensure `backend/.env` matches your frontend origin (the compose file uses `CORS_ORIGINS=http://localhost:3000`).
- **MongoDB connection**: ensure `MONGODB_URI` points to the running MongoDB instance.
- If you use Docker Compose, keep **backend** and **frontend** environment files (`backend/.env`, `frontend/.env.local`) in place.

