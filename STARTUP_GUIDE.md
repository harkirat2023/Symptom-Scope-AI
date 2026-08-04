# STARTUP GUIDE

## Quick Start

### One Command Startup

#### Linux/macOS
```bash
./boot.sh
```

#### Windows
```cmd
start.bat
```

Both scripts will:
1. ✅ Check prerequisites (MongoDB, Node.js, Python)
2. ✅ Start MongoDB (if not running)
3. ✅ Create Python virtual environment & install dependencies
4. ✅ Start FastAPI backend on port 8080
5. ✅ Wait for backend health check
6. ✅ Install npm dependencies
7. ✅ Start Next.js frontend on port 3000
8. ✅ Wait for frontend ready
9. ✅ Auto-open browser to http://localhost:3000
10. ✅ Show colored status logs

Press `Ctrl+C` to stop all services gracefully.

## Prerequisites

### Required Software
| Tool | Version | Install |
|------|---------|---------|
| MongoDB Community | 7.0+ | https://www.mongodb.com/try/download/community |
| Node.js | 18+ | https://nodejs.org/ |
| Python | 3.11+ | https://www.python.org/downloads/ |
| Git | Latest | https://git-scm.com/ |

### Verify Installation
```bash
mongod --version
node --version
npm --version
python --version
```

## Environment Setup

### Backend (.env)
```bash
cd backend
cp .env.example .env
# Edit .env with your keys:
# - MONGODB_URI (default: mongodb://localhost:27017/symptomscope)
# - GEMINI_API_KEY (required for AI features)
# - GROQ_API_KEY (optional fallback)
# - CLERK_JWKS_URL & CLERK_ISSUER (for auth)
```

### Frontend (.env.local)
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your keys:
# - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# - CLERK_SECRET_KEY
# - NEXT_PUBLIC_API_URL (default: http://localhost:8080)
```

### Clerk Authentication Setup
1. Create Clerk application at https://dashboard.clerk.com
2. Get Publishable Key and Secret Key
3. Configure Redirect URLs:
   - Sign-in: `http://localhost:3000/auth/sign-in`
   - Sign-up: `http://localhost:3000/auth/sign-up`
   - After sign-in: `http://localhost:3000/dashboard`
4. Add keys to `.env` files

### Gemini API Key
1. Get API key from https://aistudio.google.com/app/apikey
2. Add to `backend/.env` as `GEMINI_API_KEY`

### Groq API Key (Optional)
1. Get API key from https://console.groq.com
2. Add to `backend/.env` as `GROQ_API_KEY`
3. Enables fallback if Gemini fails

## Manual Startup (Development)

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### MongoDB
```bash
# Windows
mongod --dbpath "C:\data\db"

# Linux
mongod --fork --logpath /var/log/mongodb.log

# macOS
brew services start mongodb-community
```

## Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8080 |
| API Documentation | http://localhost:8080/docs |
| Health Check | http://localhost:8080/health |

## Health Check Endpoint

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": "connected",
    "ml_models": "loaded",
    "gemini_api": "configured",
    "rag_knowledge_base": "initialized"
  }
}
```

## Troubleshooting

### MongoDB Connection Failed
```bash
# Check if MongoDB is running
mongosh --eval "db.runCommand({ping:1})"

# Start MongoDB
# Windows: net start MongoDB
# Linux: sudo systemctl start mongod
# macOS: brew services start mongodb-community
```

### Backend Fails to Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Recreate virtual environment
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Build Fails
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

### Port Already in Use
```bash
# Find process on port 3000/8080
# Windows: netstat -ano | findstr :3000
# Linux/macOS: lsof -i :3000

# Kill process
# Windows: taskkill /PID <pid> /F
# Linux/macOS: kill -9 <pid>
```

### CORS Errors
- Ensure `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
- Restart backend after changes

### Authentication Issues
- Verify Clerk keys in both `.env` files
- Check Clerk dashboard for correct redirect URLs
- Ensure `NEXT_PUBLIC_CLERK_SIGN_IN_URL` and `SIGN_UP_URL` match

### AI Features Not Working
- Verify `GEMINI_API_KEY` in backend `.env`
- Check backend logs for LLM errors
- Groq fallback requires `GROQ_API_KEY`

## Project Structure

```
SymptomScope AI/
├── backend/                 # FastAPI backend
├── frontend/                # Next.js 15 frontend
├── boot.sh                  # Linux/macOS startup
├── start.bat                # Windows startup
├── CLEANUP_REPORT.md
├── RECOVERY_PLAN.md
├── PROJECT_STRUCTURE.md
├── STARTUP_GUIDE.md
├── FINAL_VERIFICATION.md
└── README.md
```

## Available Scripts

### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080 --reload  # Dev
uvicorn main:app --host 0.0.0.0 --port 8080           # Prod
pytest                                                  # Tests
```

### Frontend
```bash
cd frontend
npm run dev          # Dev server
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint
npm run test         # Vitest
```

## Production Deployment

### Environment Variables
Set all required variables in production environment:
- `MONGODB_URI` (Atlas or self-hosted)
- `GEMINI_API_KEY`
- `GROQ_API_KEY` (optional)
- `CLERK_ISSUER` & `CLERK_JWKS_URL`
- `SECRET_KEY` (strong random string)
- `CORS_ORIGINS` (production frontend URL)

### Docker (Alternative)
```bash
# Frontend
cd frontend
docker build -t symptomscope-frontend .

# Backend
cd backend
docker build -t symptomscope-backend .

# Run with docker-compose (if available)
docker compose up -d
```

### Health Checks
- Backend: `GET /health`
- Frontend: `GET /` (200 OK)

---

## Support

For issues:
1. Check backend logs for Python errors
2. Check frontend console for JS errors
3. Verify all environment variables
4. Ensure MongoDB is accessible
5. Check Clerk dashboard for auth issues