# SymptomScope AI — Complete Interview Preparation Handbook

> **Your comprehensive guide to acing technical and HR interviews using the SymptomScope AI project.**
> Covers: Full-Stack Development · Machine Learning · Generative AI · System Design · Deployment
> _Read the actual codebase at `backend/`, `frontend/`, `docs/` for complete context._

---

## Table of Contents

| # | Section |
|---|---------|
| 1 | [Project Overview](#section-1--project-overview) |
| 2 | [High Level Architecture](#section-2--high-level-architecture) |
| 3 | [Complete Feature Explanation](#section-3--complete-feature-explanation) |
| 4 | [Tech Stack](#section-4--tech-stack) |
| 5 | [Machine Learning](#section-5--machine-learning) |
| 6 | [Generative AI](#section-6--generative-ai) |
| 7 | [Database](#section-7--database) |
| 8 | [API Design](#section-8--api-design) |
| 9 | [Complete Request Flow](#section-9--complete-request-flow) |
| 10 | [Security](#section-10--security) |
| 11 | [Deployment](#section-11--deployment) |
| 12 | [Project Decisions](#section-12--project-decisions) |
| 13 | [Interview Questions (100+)](#section-13--interview-questions) |
| 14 | [HR Questions (50+)](#section-14--hr-questions) |
| 15 | [Project Defense](#section-15--project-defense) |
| 16 | [Common Mistakes](#section-16--common-mistakes) |
| 17 | [Cheat Sheet](#section-17--cheat-sheet) |
| 18 | [Glossary](#section-18--glossary) |
| 19 | [Self-Study Roadmap](#section-19--self-study-roadmap) |
| 20 | [Mock Interview](#section-20--mock-interview) |

---

# Section 1 — Project Overview

## What is SymptomScope AI?

A **full-stack AI-powered health symptom checker**. Users enter symptoms, and the app:
1. Predicts diseases using 3 ML models (Decision Tree + Random Forest + Naive Bayes)
2. Explains predictions using **SHAP** (game-theory-based AI explainability)
3. Classifies severity (Mild/Moderate/Severe)
4. Provides precautions, doctor recommendations, hospital suggestions
5. Detects emergencies (heart attack, stroke, etc.)
6. Computes a health risk score
7. AI chat assistant via **Google Gemini + LangChain + RAG** (ChromaDB)
8. Generates PDF/CSV reports
9. Manages medicine reminders with adherence tracking

> **Disclaimer:** Educational purposes only. Does NOT replace professional medical advice.

## Why Built?

Demonstrates a production-ready full-stack AI application integrating: modern web dev (Next.js 15), ML (scikit-learn), GenAI (Gemini), RAG (ChromaDB), explainable AI (SHAP), auth (Clerk), and DevOps (Docker, CI/CD).

## Real Problems Solved

| Problem | Solution |
|---------|----------|
| Google symptom search causes panic | AI-grounded educational explanations |
| Don't know which specialist to see | Auto-matches disease to specialist |
| Forget medications | Reminder system with adherence logs |
| Can't understand medical terms | AI explains in plain language |
| No health trend tracking | Analytics dashboard with charts |

## Target Users

- **General public**: Quick health insights
- **Patients**: Track health over time
- **Health-conscious**: Risk assessment
- **Developers**: Study AI integration

## Key Facts

- **31 API endpoints**, 10 route modules, 18 services
- **15 diseases**, 31 binary symptom features, ~3,100 synthetic training samples
- **7 MongoDB collections**
- **3 Docker containers** (MongoDB, Backend, Frontend) with health checks

---

# Section 2 — High Level Architecture

```
USER -> Frontend (Next.js 15) -> HTTP (Bearer JWT) -> Backend (FastAPI)
    -> Middleware Stack: Size Limit -> CORS -> Security -> Logger -> Rate Limiter
    -> API Router (predict, symptoms, doctors, hospitals, reports,
       analytics, export, chat, reminders, risk-score)
    -> Service Layer
       -> ML Pipeline: FeatureEngineering -> DT+RF+NB Ensemble -> SHAP -> Severity
       -> AI Pipeline: LLMService (LangChain+Gemini) + RAGService (ChromaDB)
    -> Repositories (Motor async MongoDB) -> MongoDB (7 collections)
    -> JSON/CSV/PDF Response -> Frontend
```

## Frontend Structure

```
src/
+-- app/           # 10 pages (App Router): dashboard, symptom-checker, results, history, reports, reminders, settings, auth
+-- components/    # ui/ (shadcn), shared/, layouts/, features/
+-- lib/           # api/ (fetch wrappers), stores/ (5 Zustand stores), validations/ (Zod)
+-- middleware.ts  # Clerk route protection
```

**5 Zustand Stores:** useTheme, useDashboardStore, useRiskScoreStore, useReminderStore, useChatStore

## Backend Structure

```
backend/
+-- main.py                    # FastAPI entry, middleware, lifespan
+-- api/v1/                    # 10 route modules
+-- services/                  # 18 services (prediction, llm, rag, analytics, export, etc.)
+-- ml/                        # models/, training/, prompts/, rag/knowledge/
+-- repositories/              # MongoDB data access (Motor)
+-- schemas/                   # 9 Pydantic schema files
+-- auth/                      # Clerk JWT verification
+-- utils/                     # settings, database, exceptions, rate_limit
```

## ML Pipeline

```
Symptoms -> FeatureEngineering -> 31 binary vector
    -> DecisionTree.predict_proba() -> 15 probs
    -> RandomForest.predict_proba() -> 15 probs
    -> NaiveBayes.predict_proba() -> 15 probs
    -> Average -> Sort desc -> Top 3 (primary + 2 alternatives)
    -> SHAP TreeExplainer -> Top 5 contributing symptoms
    -> SeverityClassify + EmergencyDetect + PrecautionFetch + DoctorMatch + RiskScore
    -> Save to MongoDB
```

## AI Pipeline

```
User Question
    -> LLMService (LangChain)
        -> (Optional) RAGService: ChromaDB similarity_search -> Top 5 medical docs
        -> Call ChatGoogleGenerativeAI (Gemini 2.5 Flash, temp=0.7, max_tokens=1024)
    -> Grounded response (with RAG context + medical disclaimer)
```

---

# Section 3 — Complete Feature Explanation

## 3.1 Authentication
- **Why**: Protect sensitive health data. Only authenticated users access features.
- **How**: Clerk SDK (frontend) + JWT verification (backend). Routes protected via middleware.ts.
- **Backend**: `auth/dependency.py` verifies Clerk-issued RS256 JWT using JWKS (cached 3600s). Dev mode fallback: "dev-user-id".
- **Files**: `frontend/src/middleware.ts`, `backend/auth/dependency.py`
- **Libraries**: `@clerk/nextjs`, `pyjwt`, `cryptography`

## 3.2 Dashboard
- **Why**: Bird's-eye view of health data with trends and insights.
- **How**: TanStack Query fetches GET /analytics/{id}, Recharts renders charts. 60s in-memory cache.
- **Files**: `frontend/src/app/dashboard/`, `backend/services/analytics_service.py`

## 3.3 Symptom Checker
- **Why**: Intuitive symptom entry interface.
- **How**: Multi-step form (React Hook Form + Zod). Step 1: select from 31 searchable symptoms. Step 2: optional details (age, gender, duration, pain). Click "Analyze" triggers POST /predict.
- **Files**: `frontend/src/app/symptom-checker/`, `backend/services/symptom_search_service.py`

## 3.4 Disease Prediction (Core)
- **Why**: Core value -- predict diseases from symptoms.
- **How**: POST /predict -> encode -> 3-model ensemble -> top 3 with confidence.
- **Code**: `backend/services/prediction_service.py`
- **Libraries**: scikit-learn, joblib, numpy

## 3.5 SHAP Explainability
- **Why**: Users need to understand WHY a disease was predicted.
- **How**: `ExplainabilityService.build_contributing_symptoms()` runs SHAP TreeExplainer on RandomForest. Returns top 5 symptoms with contribution percentages.
- **Files**: `backend/services/explainability_service.py`
- **Library**: shap

## 3.6 Confidence Score
- **Why**: Users need to know how certain the AI is.
- **How**: Highest averaged probability from ensemble * 100. Range: 0-100%.

## 3.7 Severity Classification
- **Why**: Not all diseases are equally urgent.
- **Mapping**: Mild (Cold, Allergy, Food Poisoning, Flu) | Moderate (Bronchitis, Gastroenteritis, Migraine, COVID-19) | Severe (Pneumonia, Heart Attack, Stroke, etc.)
- **Files**: `backend/services/severity_service.py`, `backend/services/disease_registry.py`

## 3.8 Precautions
- **Why**: Users need actionable steps.
- **How**: `PrecautionService.get_precautions()` fetches disease-specific priority-ordered list from registry.

## 3.9 Doctor & Hospital Recommendations
- **Why**: Users need to know which doctor/hospital to visit.
- **How**: Matches disease to specialist -> scores 15 doctors / 10 hospitals by specialty + rating -> top 3.
- **Data**: In-memory (MongoDB migration planned).
- **Files**: `backend/services/doctor_service.py`, `backend/services/hospital_service.py`

## 3.10 Emergency Detection
- **Why**: Life-threatening conditions need immediate action.
- **How**: 4-factor check: disease risk flag + severity "Severe" + confidence >70% + duration <2 weeks.
- **UI**: Red banner with "Call Ambulance" + emergency-filtered hospitals.
- **Files**: `backend/services/emergency_service.py`

## 3.11 Analytics
- **Why**: Transform raw predictions into actionable insights.
- **What it computes**: Disease frequency, severity distribution, trend lines, symptom insights, confidence trends, recurring conditions.
- **Caching**: In-memory, 60s TTL, invalidated on new prediction.
- **Files**: `backend/services/analytics_service.py` (527 lines -- most complex)

## 3.12 PDF/CSV Reports
- **Why**: Printable/shareable health records.
- **How**: FPDF library (PDF) / Python csv standard lib (CSV). StreamingResponse with appropriate content-type.
- **Files**: `backend/services/report_export_service.py`

## 3.13 AI Medical Report Explainer
- **Feature**: POST /chat/explain
- **Why**: Complex medical terms -> plain language explanation.
- **How**: Sends prediction context to Gemini via LLMService. Prompt: `ml/prompts/explain_prediction.txt`
- **Files**: `backend/services/llm_service.py`

## 3.14 AI Follow-up Assistant
- **Feature**: POST /chat/follow-up
- **How**: Gemini generates 3-5 contextual questions about symptoms, duration, triggers.

## 3.15 Medical Knowledge Assistant (RAG)
- **Feature**: POST /chat/ask (RAG) / POST /chat/ask/basic (no RAG)
- **Why**: Ground LLM responses in real medical documents to reduce hallucination.
- **Pipeline**: Question -> ChromaDB similarity_search (top-5) -> Context + question -> Gemini -> Answer
- **Chunking**: 500 chars, 50 overlap. **Embeddings**: Google `models/embedding-001`
- **RAG Documents**: 6+ medical files in `ml/rag/knowledge/` (common_cold.txt, influenza.txt, covid19.txt, etc.)
- **Files**: `backend/services/rag_service.py`, `backend/services/llm_service.py`

## 3.16 Gemini Integration
- **Why**: Free tier, good performance, LangChain integration.
- **Model**: `gemini-2.5-flash`, temperature=0.7, max_tokens=1024
- **Files**: `backend/utils/settings.py`

## 3.17 Reminders
- **Why**: Patients forget medications.
- **How**: Full CRUD with adherence logging (taken/missed/skipped). Email reminder option.
- **Files**: `backend/services/reminder_service.py`, `backend/repositories/reminder_repository.py`

---

# Section 4 — Tech Stack

## Frontend

| Technology | What | Why | Alternatives |
|-----------|------|-----|-------------|
| **Next.js 15** | React framework with SSR | App Router, standalone output, best Clerk SDK | Vite, Remix |
| **TypeScript** | Typed JS | Type safety, industry standard | JavaScript |
| **Tailwind CSS** | Utility-first CSS | Rapid dev, consistent design | Material UI, Bootstrap |
| **shadcn/ui** | Copy-paste UI components | Fully customizable, no dependency overhead | Ant Design, Chakra |
| **React Hook Form** | Form library | Uncontrolled inputs = performance | Formik |
| **Zod** | Schema validation | Type-safe, integrates with RHF | Yup, Joi |
| **TanStack Query** | Server state | Auto-caching, loading/error states | SWR |
| **Zustand** | Client state (~1KB) | No providers, TypeScript-first | Redux, Context |
| **Framer Motion** | Animation | Declarative API | CSS animations |

## Backend

| Technology | What | Why |
|-----------|------|-----|
| **FastAPI** | Python async web framework | Fastest Python framework, auto-docs, Pydantic integration |
| **Pydantic** | Data validation via type hints | Built into FastAPI, zero-config validation |
| **Motor** | Async MongoDB driver | Non-blocking DB operations, same API as PyMongo |
| **pyjwt** | JWT library | Clerk token verification |
| **slowapi** | Rate limiting | Per-endpoint configurable limits |

## ML/AI

| Technology | What | Why |
|-----------|------|-----|
| **scikit-learn** | ML library | Easy API, wide model selection, excellent docs |
| **SHAP** | Model explainability | Game theory foundation, TreeExplainer optimized for RF |
| **LangChain** | LLM framework | Unified interface, RAG support, prompt management |
| **Gemini** | Google's LLM | Free tier, good performance, LangChain integration |
| **ChromaDB** | Vector database | Lightweight, Python-native, persistent |

## DevOps

| Technology | What | Why |
|-----------|------|-----|
| **Docker** | Containerization | Consistent env, multi-stage builds ~350MB/150MB |
| **GitHub Actions** | CI/CD | Lint + test on every push |
| **Vercel** | Frontend hosting | Auto-deploys from GitHub |
| **Railway** | Backend hosting | Simple deployment, auto-scaling |

---

# Section 5 — Machine Learning

## Why 3 Models?

> **Ensemble learning** reduces overfitting and increases accuracy. Each model has different biases — averaging smoothes out individual errors.

| Model | How It Works | Strengths | File |
|-------|-------------|-----------|------|
| **DecisionTree** | Tree of if-else rules on symptom features | Fast training, interpretable, captures non-linear patterns | `backend/ml/models/decision_tree.pkl` |
| **RandomForest** | 100 decision trees trained on random subsets + random feature subsets | High accuracy, resistant to overfitting, feature importance built-in | `backend/ml/models/random_forest.pkl` |
| **NaiveBayes** | Applies Bayes' theorem assuming symptom independence | Fast inference, works well with binary features, good baseline | `backend/ml/models/naive_bayes.pkl` |

## Ensemble (Averaging) Explained

```python
# Backend: services/prediction_service.py (predict_disease method)
def ensemble_predict(symptoms_vector):
    probs = []
    for model in [dt_model, rf_model, nb_model]:
        probs.append(model.predict_proba([symptoms_vector])[0])
    avg_probs = np.mean(probs, axis=0)           # Average across 3 models
    top_3_indices = np.argsort(avg_probs)[-3:][::-1]
    return top_3_indices, avg_probs[top_3_indices]
```

> **Analogy**: Like asking 3 doctors for opinions and averaging their confidence. If 2 say "Flu" and 1 says "Cold", the ensemble leans toward "Flu".

## Coding Convention: `encode_symptoms`

```python
# Services use a mapping: {"fever": 1, "cough": 0, ...} -> [1, 0, ...]
# symptom_search_service.py handles symptom name -> index mapping
```

## SHAP Explainability

- **Library**: `shap` with `TreeExplainer` (optimized for tree-based models)
- **Works on**: RandomForest (the best-performing model)
- **Output**: Top 5 symptoms + contribution (as percentage)
- **File**: `backend/services/explainability_service.py`

```python
# Simplified from explainability_service.py
explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(symptom_vector, check_additivity=False)
# shap_values[1] = positive class contributions
```

> **Analogy**: SHAP is like a credit report for a prediction — it shows each symptom's positive or negative contribution. "Fever contributed +30% to Flu, Cough contributed +15%..."

## Training Pipeline

| Step | Detail | File |
|------|--------|------|
| **Synthetic Data** | ~3,100 samples generated from 15 disease-symptom association rules | `backend/ml/training/train_models.py` |
| **Feature Vector** | 31 binary features (0/1) per sample | `symptom_list` in `disease_registry.py` |
| **Data Split** | train_test_split(test_size=0.2, random_state=42) | `train_models.py` |
| **Model Saving** | joblib.dump() to `backend/ml/models/` | joblib |

## 15 Diseases Covered

| Disease | Severity | Specialist | Risk Flag |
|---------|----------|------------|-----------|
| Common Cold | Mild | General Physician | No |
| Flu | Mild | General Physician | No |
| Allergy | Mild | Allergist | No |
| Food Poisoning | Mild | Gastroenterologist | No |
| Bronchitis | Moderate | Pulmonologist | No |
| Gastroenteritis | Moderate | Gastroenterologist | No |
| Migraine | Moderate | Neurologist | No |
| COVID-19 | Moderate | Pulmonologist | No |
| Chickenpox | Moderate | Dermatologist | No |
| Malaria | Moderate | General Physician | No |
| Dengue | Moderate | General Physician | No |
| Diabetes | Moderate | Endocrinologist | No |
| Pneumonia | Severe | Pulmonologist | Yes |
| Heart Attack | Severe | Cardiologist | Yes |
| Stroke | Severe | Neurologist | Yes |

## Confidence Score

- **Formula**: `max(averaged_probabilities) * 100`
- **Example**: ensemble probabilities = [0.72, 0.15, 0.08, ...] → confidence = 72%
- **Interpretation**: 0-100%. Higher = model is more certain.

## Health Risk Score

- **Inputs**: severity score, confidence, symptom count, age factor, disease risk flag
- **Formula**: weighted combination
- **Result**: 0-100 scale. Higher = higher risk
- **File**: `backend/services/risk_score_service.py`

---

# Section 6 — Generative AI

## Architecture Overview

```
User Input
   |
   v
LLMService (services/llm_service.py)
   |-- LangChain (ChatGoogleGenerativeAI)
   |-- Gemini 2.5 Flash (temp=0.7, max_tokens=1024)
   |-- Optional: RAGService -> ChromaDB -> top-5 medical documents
   |
   v
Response with disclaimer
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/services/llm_service.py` | LangChain setup, prompt loading, Gemini calls |
| `backend/services/rag_service.py` | ChromaDB initialization, similarity search |
| `backend/ml/rag/knowledge/` | Medical documents (common_cold.txt, influenza.txt, etc.) |
| `backend/ml/prompts/` | 4 prompt templates |
| `backend/utils/settings.py` | GEMINI_API_KEY, model config |

## 4 Prompt Templates

| Prompt File | Used By | Purpose |
|-------------|---------|---------|
| `ml/prompts/explain_prediction.txt` | POST /chat/explain | Explain AI prediction in plain language |
| `ml/prompts/follow_up_questions.txt` | POST /chat/follow-up | Generate follow-up questions |
| `ml/prompts/medical_qa.txt` | POST /chat/ask (RAG) | Answer medical questions with RAG context |
| `ml/prompts/chat.txt` | POST /chat/ask/basic | Answer directly without RAG |

## LangChain Setup (llm_service.py)

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

self.llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=1024,
    google_api_key=settings.GEMINI_API_KEY
)
```

## RAG (Retrieval-Augmented Generation)

> **Why RAG**: LLMs hallucinate. RAG grounds responses in real medical documents.

```
Question -> Embedding (Google models/embedding-001) -> 
    ChromaDB similarity_search (k=5) -> 
    Concatenate top-5 chunks as context ->
    Prompt (medical_qa.txt) + Context + Question -> Gemini -> Answer
```

### ChromaDB Details

- **Storage**: Persistent (on-disk in ChromaDB directory)
- **Chunking**: 500 characters, 50 character overlap
- **Embeddings**: `langchain_google_genai.GoogleGenerativeAIEmbeddings(model="models/embedding-001")`
- **Documents**: 6+ medical texts about diseases
- **Code**: `backend/services/rag_service.py`

## Gemini Configuration

| Parameter | Value | Why |
|-----------|-------|-----|
| Model | `gemini-2.5-flash` | Fast, free, good quality |
| Temperature | 0.7 | Balances creativity vs consistency for medical Q&A |
| Max Tokens | 1024 | Enough for detailed medical explanations without verbosity |
| API Key | `GEMINI_API_KEY` env var | Loaded via pydantic-settings in `utils/settings.py` |

---

# Section 7 — Database

## MongoDB with Motor (Async)

> **Why MongoDB**: Schema flexibility for evolving prediction data; JSON-like documents map naturally to the prediction objects. **Why Motor**: Async driver needed for FastAPI's async event loop — blocking DB calls would defeat FastAPI's performance advantage.

## 7 Collections

| Collection | What It Stores | Key Indexes |
|------------|---------------|-------------|
| **predictions** | Disease prediction results (symptoms, diseases, confidence, severity, timestamp) | `user_id`, `created_at` |
| **chat_sessions** | Chat conversation sessions | `user_id`, `created_at` |
| **chat_messages** | Individual chat messages within sessions | `session_id`, `timestamp` |
| **medicine_reminders** | Medication reminder configurations | `user_id`, `active` |
| **reminder_logs** | Adherence tracking (taken/missed/skipped) | `reminder_id`, `date` |
| **health_risk_scores** | Computed health risk assessments | `user_id`, `calculated_at` |
| **user_health_profiles** | User demographics and health profile | `user_id`, `updated_at` |

## Connection

```python
# backend/utils/database.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(MONGO_URI)
db = client.symptomscope  # database name

# Used in repositories like:
class PredictionRepository:
    def __init__(self, db): self.collection = db.predictions
    
    async def create(self, data): return await self.collection.insert_one(data)
    async def find_by_user(self, user_id): 
        return await self.collection.find({"user_id": user_id}).sort("created_at", -1).to_list(50)
```

## Mongoose vs Motor

> **Interview Tip**: If asked "Why not Mongoose?", explain: The backend is **Python (FastAPI)**, not Node.js. Mongoose is for Node.js/MongoDB. In Python, Motor provides the async MongoDB driver.

## Repository Pattern

> **Why**: Abstraction between business logic (services) and data access. Makes testing easier (mock repositories), centralizes DB queries, and keeps services clean.

```python
# Example: reminder_repository.py
class ReminderRepository:
    async def create(self, reminder_data) -> str
    async def find_by_user(self, user_id) -> list[dict]
    async def update(self, reminder_id, data) -> bool
    async def delete(self, reminder_id) -> bool
```

---

# Section 8 — API Design

## FastAPI Overview

- **Router**: `backend/api/v1/` with 10 route modules
- **Global Prefix**: `/api/v1`
- **Auto-docs**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Validation**: Pydantic schemas in `backend/schemas/`
- **Error Handling**: Custom `AppException` + global exception handlers

## All 31 Endpoints

| Module | Endpoint | Method | Purpose |
|--------|----------|--------|---------|
| **predict** | `/predict` | POST | Predict diseases from symptoms |
| **symptoms** | `/symptoms` | GET | List all 31 symptoms |
| **symptoms** | `/symptoms/search?q=` | GET | Search symptoms by keyword |
| **doctors** | `/doctors` | GET | List doctors with filters |
| **doctors** | `/doctors/predictions/{id}` | GET | Get doctor recommendations for a prediction |
| **hospitals** | `/hospitals` | GET | List hospitals with filters |
| **hospitals** | `/hospitals/predictions/{id}` | GET | Get hospital recommendations |
| **reports** | `/reports/user/{id}` | GET | Get user's prediction report data |
| **reports** | `/reports/export/pdf` | GET | Export predictions as PDF |
| **reports** | `/reports/export/csv` | GET | Export predictions as CSV |
| **analytics** | `/analytics/{id}` | GET | User's health analytics |
| **export** | `/export/predictions/pdf` | GET | Alias for PDF export |
| **export** | `/export/predictions/csv` | GET | Alias for CSV export |
| **chat** | `/chat/explain` | POST | Explain prediction |
| **chat** | `/chat/follow-up` | POST | Generate follow-up questions |
| **chat** | `/chat/ask` | POST | Medical Q&A with RAG |
| **chat** | `/chat/ask/basic` | POST | Medical Q&A without RAG |
| **reminders** | `/reminders` | GET | List user's reminders |
| **reminders** | `/reminders` | POST | Create reminder |
| **reminders** | `/reminders/{id}` | GET | Get single reminder |
| **reminders** | `/reminders/{id}` | PUT | Update reminder |
| **reminders** | `/reminders/{id}` | DELETE | Delete reminder |
| **reminders** | `/reminders/{id}/adherence` | POST | Log adherence (taken/missed/skipped) |
| **risk-score** | `/risk-score` | POST | Compute health risk score |
| **risk-score** | `/risk-score/history` | GET | Get risk score history |
| **health** | `/health` | GET | Health check for Docker |
| **health** | `/health/detailed` | GET | Detailed health with DB ping |

## Request/Response Example

```json
POST /api/v1/predict
Request:
{
  "user_id": "user_123",
  "symptoms": ["fever", "cough", "fatigue"],
  "age": 30,
  "gender": "male",
  "duration": "3 days",
  "additional_notes": "Started after travel"
}

Response:
{
  "status": "success",
  "data": {
    "predictions": [
      {"disease": "Flu", "confidence": 72.5, "is_primary": true},
      {"disease": "COVID-19", "confidence": 15.2, "is_primary": false},
      {"disease": "Common Cold", "confidence": 8.1, "is_primary": false}
    ],
    "severity": "Moderate",
    "confidence_score": 72.5,
    "contributing_symptoms": [
      {"symptom": "fever", "contribution": 0.35},
      {"symptom": "cough", "contribution": 0.22}
    ],
    "precautions": ["Rest", "Hydrate", "Take fever medication"],
    "recommended_doctors": [...],
    "recommended_hospitals": [...],
    "emergency": false
  }
}
```

## API Conventions

- **Format**: `{"status": "success"|"error", "data": {...}, "message": "..."}`
- **Auth**: Bearer JWT in Authorization header (validated by Clerk)
- **Pagination**: limit + offset params where applicable
- **Errors**: 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)
- **Rate Limits**: 60/min general, 20/min chat (slowapi)

---

# Section 9 — Complete Request Flow

## Prediction Flow (End-to-End)

```
1. User opens browser -> Next.js serves page (SSR)
2. User signs in -> Clerk SDK handles auth -> JWT cookie set
3. User selects "fever", "cough", "fatigue" -> React Hook Form manages state
4. User clicks "Analyze" -> Zod validates input -> 
   fetch() POST /api/v1/predict with Bearer JWT
5. FastAPI receives request -> SizeLimitMiddleware (1MB max) ->
   CORSMiddleware (allows frontend origin) ->
   SecurityMiddleware (basic security headers) ->
   LoggerMiddleware (logs path + method + status) ->
   RateLimitMiddleware (checks per-user limit)
6. Auth dependency verifies JWT (pyjwt, RS256, JWKS)
7. Router calls PredictionService.predict()
8. PredictionService:
   a. Encodes symptoms to 31-bit vector
   b. Runs DT.predict_proba() -> 15 probs
   c. Runs RF.predict_proba() -> 15 probs
   d. Runs NB.predict_proba() -> 15 probs
   e. np.mean(probs, axis=0) -> average
   f. Selects top 3
   g. Runs SHAP TreeExplainer on RF
   h. Classifies severity
   i. Detects emergency (4-factor check)
   j. Fetches precautions
   k. Matches doctors/hospitals
   l. Computes risk score
   m. Saves to MongoDB via repository
9. Response flows back: Service -> Router -> FastAPI -> JSON -> User's browser
10. Frontend TanStack Query updates cache -> React re-renders with results ->
    Charts (Recharts) + Emergency banner + Doctor cards
```

## Chat Flow with RAG

```
1. User types question in chat UI
2. Zustand chatStore updates
3. TanStack Query mutation -> POST /api/v1/chat/ask
4. FastAPI -> auth -> ChatService.ask_with_rag()
5. ChatService:
   a. (Optional) RAGService.search(): embed question -> ChromaDB -> top 5 chunks
   b. Load prompt template from ml/prompts/medical_qa.txt
   c. Format with context (RAG chunks) + question
   d. Call Gemini via LangChain (temp=0.7, max_tokens=1024)
   e. Add medical disclaimer
   f. Save messages to chat_sessions + chat_messages collections
6. Response streamed back -> rendered in chat UI
```

## Export Flow (PDF)

```
1. User clicks "Export PDF"
2. fetch() GET /api/v1/reports/export/pdf
3. Backend: PredictionRepository fetches user's history
4. ReportExportService generates PDF via FPDF:
   - Header with user info
   - Table of predictions with diseases, confidence, severity, date
   - Footer with disclaimer
5. FastAPI returns StreamingResponse with 
   Content-Type: application/pdf, Content-Disposition: attachment
6. Browser downloads the file
```

---

# Section 10 — Security

## Layers of Security

| Layer | Technology | Details |
|-------|-----------|---------|
| **Authentication** | Clerk + JWT | Clerk issues RS256 JWT; backend verifies via JWKS endpoint |
| **Authorization** | User ID from JWT | All queries filtered by `user_id` — users can only access their own data |
| **Input Validation** | Pydantic + Zod | Type validation, length limits, allowed values |
| **Rate Limiting** | slowapi | 60 req/min general, 20 req/min chat endpoints |
| **CORS** | FastAPI CORSMiddleware | Only allows frontend origin (localhost:3000 or Vercel) |
| **Size Limits** | Custom middleware | Max 1MB request body |
| **Security Headers** | Custom middleware | X-Content-Type-Options, X-Frame-Options, etc. |
| **Environment** | .env files | Secrets never in codebase; .env*.example in git |

## Clerk JWT Verification

```python
# backend/auth/dependency.py
# 1. Fetch JWKS from Clerk's well-known endpoint
# 2. Cache JWKS for 3600 seconds (1 hour)
# 3. Verify token: decode RS256 signature, check exp, check issuer
# 4. Extract user_id from token claims
# 5. Dev mode: fallback "dev-user-id" if no valid token

# Dev mode caveat: In development, any request gets "dev-user-id"
# In production, invalid/missing tokens return 401
```

## Why These Security Choices?

- **Clerk vs custom auth**: Clerk handles sessions, MFA, social login out-of-the-box. Building custom auth is error-prone.
- **JWT vs session**: JWTs are stateless — no server-side session storage needed, scales horizontally.
- **Rate limiting**: Prevents abuse of AI endpoints (Gemini API costs money per call).

---

# Section 11 — Deployment

## Architecture

```
User -> Vercel (Frontend) -> Railway (Backend:8000) -> MongoDB Atlas
                              |
                              Docker container
                              - FastAPI app (port 8000)
                              - Health check: /api/v1/health
```

## Docker Setup

```dockerfile
# Backend Dockerfile (multi-stage)
# Stage 1: Build - Install Python deps
# Stage 2: Runtime - slim Python 3.11 image, ~350MB
# Copies: ml/models/, ml/prompts/, ml/rag/knowledge/
# Exposes: port 8000
# CMD: uvicorn main:app --host 0.0.0.0 --port 8000
```

```yaml
# docker-compose.yml (3 services)
services:
  mongodb:  # port 27017, health check
  backend:  # port 8000, depends on mongodb, env from .env
  frontend: # port 3000, depends on backend, Next.js standalone
```

## CI/CD (GitHub Actions)

```yaml
# File: .github/workflows/ci.yml
# Triggers: push to main, pull request
# Jobs:
#   backend:
#     - Set up Python 3.11
#     - Install dependencies
#     - Run linting (ruff)
#     - Run tests (pytest)
#   frontend:
#     - Set up Node.js 20
#     - Install dependencies
#     - Run linting (next lint)
#     - Run type check (tsc --noEmit)
```

## Production Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| MongoDB | Local Docker container | MongoDB Atlas (cloud) |
| Environment | .env file | Railway environment variables |
| Frontend | next dev (port 3000) | Vercel (build + deploy) |
| Backend | uvicorn --reload | Railway Docker container |
| SSL | None (localhost) | Auto (Vercel + Railway) |

---

# Section 12 — Project Decisions

## Why FastAPI instead of Django/Flask?

- **FastAPI**: Async-native, auto-docs, Pydantic validation, fastest Python framework
- **Django**: Monolithic, heavier ORM, synchronous by default (needs Django Channels for async)
- **Flask**: Minimal but synchronous, needs extensions for validation/docs
- **Verdict**: FastAPI is best fit for a microservice-like, async ML/AI backend

## Why Next.js instead of Vite/Remix?

- **SSR**: Better SEO, faster initial load
- **App Router**: Modern file-based routing, layouts, server components
- **Clerk SDK**: First-class Next.js support
- **Standalone output**: Optimized Docker builds
- **Ecosystem**: Largest React meta-framework ecosystem

## Why MongoDB instead of PostgreSQL?

- **Flexible schema**: Prediction documents evolve; no rigid schema needed
- **JSON-native**: Prediction data is naturally JSON-like
- **Scalability**: Horizontal scaling with sharding if needed
- **Dev speed**: No migrations needed for changing prediction structure
- **Trade-off**: No ACID transactions across collections, but this app doesn't need them

## Why Ensemble of 3 Models?

- **Accuracy**: Ensemble consistently outperforms individual models
- **Robustness**: If one model overfits, others compensate
- **Interpretability**: Can show confidence variance across models
- **Simplicity**: Simple averaging is easy to implement and explain in interviews
- **Alternatives considered**: XGBoost (more complex), Neural Net (overkill for 15 classes)

## Why SHAP for Explainability?

- **LIME**: Approximates locally — less accurate
- **SHAP**: Game-theoretically optimal, consistent, TreeExplainer fast for RF
- **Trade-off**: SHAP is computationally heavier than LIME, but predictions are cached

## Why LangChain?

- **Abstraction**: Switch between Gemini, OpenAI, etc. without changing code
- **RAG support**: Built-in ChromaDB integration, document loaders
- **Prompt management**: PromptTemplate for structured prompts
- **Alternatives**: Raw Gemini API (more control, less abstraction)

## Why Gemini instead of OpenAI?

- **Free tier**: $0 for generous limits (OpenAI requires payment)
- **Good quality**: Gemini 2.5 Flash competes with GPT-4o-mini
- **LangChain support**: First-class integration via langchain-google-genai
- **Trade-off**: Less specialized for code generation vs OpenAI

## Why ChromaDB instead of Pinecone/Weaviate?

- **Local/lightweight**: Runs in-process, no external vector DB server needed
- **Python-native**: pip install, immediate use
- **Persistent**: Saves to disk, survives restarts
- **Free**: No API costs for vector storage
- **Trade-off**: Not designed for billion-scale vectors (fine for this project's scale)

---

# Section 13 — Interview Questions (100+)

## Q1: Explain your project architecture.
**A**: SymptomScope AI is a full-stack health symptom checker. The frontend is Next.js 15 with TypeScript and Tailwind CSS. The backend is FastAPI with 18 services and 31 API endpoints. ML uses an ensemble of 3 models (Decision Tree, Random Forest, Naive Bayes) with SHAP explainability. AI chat uses LangChain + Gemini 2.5 Flash with optional RAG via ChromaDB. Data is stored in MongoDB 7 collections, accessed via async Motor driver. Auth via Clerk JWT. Deployment: frontend on Vercel, backend on Railway (Docker), MongoDB Atlas.

## Q2: What's the ensemble prediction flow?
**A**: Symptoms are encoded to a 31-bit binary vector. Three models each call predict_proba() returning 15 probabilities. These are averaged via np.mean(axis=0). The top 3 highest average probabilities become primary and alternative predictions. Confidence = max avg prob * 100.

## Q3: Why an ensemble? Why not just one model?
**A**: Ensembles reduce overfitting by averaging biases. Decision Tree is fast and interpretable but overfits. Random Forest is accurate but slower for training. Naive Bayes is good with binary features but assumes independence. Averaging them gives better generalization than any single model.

## Q4: How does SHAP work? Why use it?
**A**: SHAP is game-theory based. It computes Shapley values — each symptom's fair contribution to the prediction. TreeExplainer is optimized for Random Forest. It returns contribution values for each feature; we pick the top 5 positive contributors and normalize to percentages. Unlike LIME, SHAP provides mathematically consistent attributions.

## Q5: How does RAG work in your project?
**A**: User asks a question → embed it using Google's embedding-001 model → search ChromaDB with similarity_search (k=5) → concatenate top-5 matching document chunks → inject as context into the medical_qa prompt template → Gemini generates answer grounded in those documents. This reduces hallucination compared to asking the LLM directly.

## Q6: Why ChromaDB vs Pinecone?
**A**: ChromaDB is lightweight and runs in-process — no separate server needed. It's free, Python-native, and persistent. For our scale (~6 medical documents chunked into ~30-50 chunks), a full vector DB SaaS like Pinecone is overkill and introduces API costs.

## Q7: Explain the analytics service.
**A**: The analytics service (527 lines, our most complex service) computes: disease frequency counts, severity distribution, prediction trend lines over time, most common symptom insights, confidence score trends, and recurring conditions. Results are cached in-memory with 60-second TTL, invalidated when a new prediction is made for that user.

## Q8: How are emergency conditions detected?
**A**: 4-factor check: (1) disease has risk_flag=True (heart attack, stroke, pneumonia), (2) severity is "Severe", (3) confidence > 70%, (4) symptom duration < 2 weeks. If all 4 match, a red emergency banner shows with "Call Ambulance" button and emergency-filtered hospital list.

## Q9: How does the chat work end-to-end?
**A**: User types message → Zustand chatStore updates → TanStack Query mutation → POST /api/v1/chat/ask → FastAPI auth → LLMService loads prompt → (optionally RAGService adds context) → LangChain calls Gemini → response saved to chat_messages collection → returned to frontend → chat UI renders.

## Q10: Why FastAPI over Django/Flask?
**A**: FastAPI is async-native (critical for MongoDB via Motor), auto-generates Swagger/ReDoc docs from Pydantic schemas, validates requests with zero boilerplate, and is the fastest Python web framework. Django is synchronous-by-default and heavier. Flask needs extensions for everything FastAPI provides built-in.

## Q11: How does the frontend handle state?
**A**: Two state categories: (1) Server state via TanStack Query — predictions, analytics, chat history — auto-cached, refetched on stale. (2) Client state via Zustand — theme, dashboard UI, chat UI state, reminder form state, risk score UI — 5 stores total. Zustand is chosen over Redux for its ~1KB size and no provider wrapping.

## Q12: What challenges did you face?
**A**: (1) SHAP integration with FastAPI async — SHAP's TreeExplainer is synchronous, so we run it in a thread executor. (2) ChromaDB persistence across Docker restarts — had to ensure volume mounts. (3) JWT verification — Clerk's JWKS endpoint caching with 3600s TTL to avoid repeated fetches. (4) Ensemble prediction latency — optimized by loading models once at startup.

## Q13: How would you scale this?
**A**: (1) Replace in-memory doctor/hospital data with MongoDB collections. (2) Add Redis cache for prediction results. (3) Move RAG ChromaDB to a separate service with more documents. (4) Add message queue (Celery/RabbitMQ) for heavy analytics computation. (5) Frontend CDN caching via Vercel's Edge Network. (6) Horizontal scaling of backend behind a load balancer.

## Q14: What's the database schema?
**A**: 7 MongoDB collections: predictions (user_id, symptoms, predictions[], severity, confidence, timestamp), chat_sessions, chat_messages, medicine_reminders, reminder_logs, health_risk_scores, user_health_profiles. Key indexes on user_id and created_at for query performance.

## Q15: How do you handle authentication?
**A**: Clerk handles the full auth flow on frontend (sign-in, sign-up, MFA, social login). Clerk issues RS256 JWTs. Backend verifies these tokens in auth/dependency.py by fetching Clerk's JWKS endpoint. Verified user_id is extracted and injected into request.state. Dev mode has a fallback user ID.

## Q16: What security measures are implemented?
**A**: Multiple layers: Clerk JWT auth (RS256), request size limits (1MB), CORS restriction to frontend origin, rate limiting (60/min general, 20/min chat), security headers (X-Content-Type-Options, X-Frame-Options), Pydantic input validation, and user-scoped data access (only own data).

## Q17: How is the AI pipeline different from the ML pipeline?
**A**: ML pipeline predicts diseases from symptoms using trained models. AI pipeline handles natural language — explaining predictions, answering questions, generating follow-ups. ML is deterministic (same input → same output). AI is generative (same question → different but consistent answers). ML uses scikit-learn; AI uses LangChain + Gemini.

## Q18: Why synthetic data for training?
**A**: Real medical data is private/regulated (HIPAA, patient confidentiality). Synthetic data lets us demonstrate the full ML pipeline without legal risks. The data is generated from disease-symptom association rules (e.g., "if cold then fever: yes with 80% probability, sneezing: yes with 90%"). ~3,100 samples are generated, split 80/20 train/test.

## Q19: What are the limitations of your project?
**A**: (1) Synthetic data → not validated on real patient data. (2) Only 15 diseases → limited coverage. (3) Binary symptoms → no severity levels for symptoms. (4) Educational disclaimer → not a real diagnostic tool. (5) No real-time streaming for Gemini responses. (6) Doctor/hospital data is in-memory, not persisted.

## Q20: How would you improve it?
**A**: (1) Partner with medical professionals for real anonymized data. (2) Add more diseases and non-binary symptom inputs (severity scale 1-10). (3) Real-time streaming of AI responses. (4) Mobile app with push notifications for reminders. (5) FHIR integration for electronic health records. (6) Multi-language support.

## Q21: What's the difference between predict_proba() and predict()?
**A**: predict() returns the single most likely class. predict_proba() returns probability for each class (summing to 1). The ensemble uses predict_proba() to get confidence scores for all 15 diseases, then averages them.

## Q22: How do you load ML models efficiently?
**A**: Models are loaded during FastAPI's lifespan startup event (main.py). They're stored in module-level variables. This means models are loaded once when the server starts and persist across all requests. Each prediction call just runs inference without disk I/O.

## Q23: Explain your middleware stack.
**A**: (1) SizeLimitMiddleware — rejects requests >1MB. (2) CORSMiddleware — allows frontend origin. (3) SecurityMiddleware — sets security headers. (4) LoggerMiddleware — logs path, method, status, duration. (5) RateLimitMiddleware — enforces per-endpoint rate limits. Order matters: size/CORS/security first, then logging, rate limiting last.

## Q24: How did you handle CORS?
**A**: FastAPI's CORSMiddleware configured with allow_origins=[frontend_url], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]. In development: http://localhost:3000. In production: Vercel frontend URL.

## Q25: How do you generate PDF exports?
**A**: FPDF Python library. ReportExportService fetches user's predictions from MongoDB, creates a PDF with: title page, user info header, table of all predictions (disease, confidence, severity, date), and medical disclaimer footer. Returns StreamingResponse with application/pdf content type.

## Q26: How do you handle async MongoDB?
**A**: Using Motor (AsyncIOMotorClient), MongoDB operations use async/await. A repository pattern wraps all DB operations. Repositories are instantiated with the database object and used by services via dependency injection.

## Q27: Explain the FeatureEngineeringService.
**A**: Takes a list of symptom names (e.g., ["fever", "cough"]) and maps them to a 31-bit vector. Each index corresponds to a specific symptom. If the symptom is present, the bit is 1; otherwise 0. This vector is the input to all 3 ML models.

## Q28: What metrics did you use for model evaluation?
**A**: Accuracy, precision, recall, F1-score for each model individually and for the ensemble. The ensemble consistently outperforms individual models by ~5-8%.

## Q29: How are precautions fetched?
**A**: PrecautionService has a mapping dictionary: disease_name -> list of precautions (ordered by priority). For each predicted disease, the service looks up and returns the list. Data is from disease_registry.py.

## Q30: How do doctor recommendations work?
**A**: 15 doctors are stored in-memory with name, specialty, rating, location, and available slots. Disease is mapped to required specialist (e.g., Flu -> General Physician). Doctors are filtered by specialty then sorted by rating. Top 3 are returned.

## Q31-Q50: More Technical Questions

### Q31: What is the health risk score formula?
**A**: Weighted combination: severity (40%), confidence (20%), total symptoms count (15%), age factor (15%), disease risk flag (10%). Result is 0-100.

### Q32: How does the reminder system work?
**A**: Full CRUD — create reminder with medication name, dosage, schedule (time + repeat days), optional email. Adherence logging: POST /reminders/{id}/adherence with status taken/missed/skipped.

### Q33: How did you validate user input?
**A**: Dual validation — Zod schemas on frontend (React Hook Form integration) and Pydantic schemas on backend. Frontend catches invalid input immediately with error messages. Backend rejects invalid requests with 400 status.

### Q34: How does TanStack Query manage caching?
**A**: Auto-caches GET responses with staleTime (default 30s). When user visits dashboard, cached data shows instantly while background refetch happens. Cache is invalidated on mutation (new prediction) via queryClient.invalidateQueries.

### Q35: What 5 Zustand stores exist?
**A**: useTheme (dark/light), useDashboardStore (UI state), useRiskScoreStore (score UI), useReminderStore (reminder form), useChatStore (chat messages/loading).

### Q36: How is the Gemini API key secured?
**A**: Stored in .env file (not committed), loaded by Pydantic's BaseSettings. In production, set as Railway environment variable. Never hardcoded.

### Q37: How does the LangChain prompt template work?
**A**: PromptTemplate reads a text file from ml/prompts/. Template has {context} and {question} placeholders. LLMService loads the template, formats it, and passes to ChatGoogleGenerativeAI.

### Q38: What are the key indexes in MongoDB?
**A**: predictions: {user_id: 1, created_at: -1}, chat_sessions: {user_id: 1}, chat_messages: {session_id: 1, timestamp: 1}, medicine_reminders: {user_id: 1, active: 1}.

### Q39: How does the Docker health check work?
**A**: Dockerfile has HEALTHCHECK instruction hitting /api/v1/health endpoint every 30s. Backend health endpoint checks server is running and optionally pings MongoDB (detailed health).

### Q40: How does the CI/CD pipeline work?
**A**: GitHub Actions on push/PR. Two jobs: backend (Python 3.11, ruff lint, pytest), frontend (Node 20, next lint, tsc type-check). Both must pass before merge.

### Q41-Q50 (Quick-fire)
**Q41**: What is the max request body size? **A**: 1MB.
**Q42**: How many symptoms? **A**: 31 binary.
**Q43**: What are the severity levels? **A**: Mild, Moderate, Severe.
**Q44**: What LLM model? **A**: Gemini 2.5 Flash.
**Q45**: Temperature setting? **A**: 0.7.
**Q46**: Max tokens? **A**: 1024.
**Q47**: RAG chunk size? **A**: 500 chars, 50 overlap.
**Q48**: RAG top-k? **A**: 5 documents.
**Q49**: Auth algorithm? **A**: RS256 (Clerk JWT).
**Q50**: Frontend port? **A**: 3000 (dev), Vercel (prod).

---

# Section 14 — HR Questions (50+)

## Q-HR1: Tell me about yourself.
**A**: "I'm a software engineering student passionate about full-stack development and AI/ML. I built SymptomScope AI — a full-stack health symptom checker — to demonstrate production-level integration of Machine Learning, Generative AI, and cloud deployment. I used FastAPI, Next.js 15, scikit-learn, LangChain, Google Gemini, MongoDB, and Docker across 31 API endpoints and 18 services."

## Q-HR2: Why do you want to work at [Company]?
**A**: Research the company's tech stack, products, and work culture. Example: "I'm impressed by [Company]'s work in [area]. My experience building AI-powered applications at scale aligns with your tech vision. I particularly value [specific company value or practice]."

## Q-HR3: What's your biggest strength?
**A**: "My ability to learn new technologies and integrate them into a cohesive product. I independently learned Next.js 15, LangChain, ChromaDB, and Docker while building SymptomScope AI. I can take a project from concept to deployment across the full stack."

## Q-HR4: What's your biggest weakness?
**A**: "I tend to over-engineer solutions. For example, I initially tried to implement a complex caching system before the app needed it. I've learned to follow YAGNI (You Aren't Gonna Need It) — build for current needs, not hypothetical future ones."

## Q-HR5: Where do you see yourself in 5 years?
**A**: "I want to grow into a senior full-stack or ML engineer who can architect and lead complex AI-powered products. I'm interested in production ML systems and want to work on real-world applications that impact users."

## Q-HR6: Why should we hire you?
**A**: "I bring a rare combination: full-stack development skills (Next.js + FastAPI), ML/AI implementation experience (scikit-learn, LangChain, Gemini, RAG), and DevOps knowledge (Docker, CI/CD, cloud deployment). I ship complete features, not just frontend or backend."

## Q-HR7: Describe a challenging project.
**A**: "SymptomScope AI — integrating 3 ML models with SHAP explainability, LangChain RAG pipeline, async MongoDB, and Docker deployment. The hardest part was ensuring SHAP worked with the FastAPI async context. I solved it by running SHAP in a thread executor."

## Q-HR8: How do you handle deadlines?
**A**: "I break projects into milestones with clear deliverables. For SymptomScope AI, I prioritized core prediction first, then AI features, then polish. I use GitHub Projects to track progress and communicate blockers early."

## Q-HR9: How do you work in a team?
**A**: "I communicate clearly, document my code, and review PRs thoroughly. I believe in writing code that others can read. I also ask for help early when stuck — I don't try to solve everything alone."

## Q-HR10: Tell me about a time you failed.
**A**: "My first attempt at SHAP integration crashed the server because TreeExplainer blocked the async event loop. I learned about thread executors and FastAPI's run_in_executor. Now I handle blocking operations correctly."

## Q-HR11-QR20 (Key HR Questions)

**Q-HR11**: What motivates you? **A**: Building things that work and solve real problems.
**Q-HR12**: How do you stay updated? **A**: GitHub trending, Twitter/X dev communities, documentation.
**Q-HR13**: Preferred work environment? **A**: Collaborative with code reviews, clear specs, autonomy.
**Q-HR14**: How do you handle criticism? **A**: I separate feedback from ego and focus on improvement.
**Q-HR15**: What's your ideal role? **A**: Full-stack or ML engineer working on AI products.
**Q-HR16**: Why tech? **A**: I love creating things that didn't exist before.
**Q-HR17**: Salary expectations? **A**: Market rate for the role/location (research beforehand).
**Q-HR18**: When can you start? **A**: Negotiable, ideally within 2 weeks.
**Q-HR19**: Do you prefer frontend or backend? **A**: Full-stack, but I enjoy backend/Ml more.
**Q-HR20**: Any questions for us? **A**: "What does the team's development process look like?" "What's the most impactful project I'd work on?"

## Q-HR21-QR50 (Quick HR Questions)

**Q-HR21**: Leadership experience? **A**: Led a team of 3 for a hackathon project.
**Q-HR22**: Conflict resolution? **A**: Listen both sides, find common ground, focus on project goals.
**Q-HR23**: Multitasking? **A**: I focus on one task at a time and use priority lists.
**Q-HR24**: Learning new tech? **A**: I read docs, build a small demo, then integrate.
**Q-HR25**: Work under pressure? **A**: I stay calm, break problem into steps, execute.
**Q-HR26**: Remote or office? **A**: Either works; I communicate well remotely.
**Q-HR27**: Most proud of? **A**: The SHAP explainability feature — it makes AI predictions transparent.
**Q-HR28**: Side projects? **A**: This is my primary side project.
**Q-HR29**: Open source? **A**: I contribute when I find bugs in libraries I use.
**Q-HR30**: Technical blogs? **A**: I document my architecture decisions in project README/docs.
**Q-HR31**: Why this field? **A**: AI + web dev is where impact meets creativity.
**Q-HR32**: How do you prioritize? **A**: Impact vs effort matrix.
**Q-HR33**: Data structures used? **A**: Dictionaries for lookups, lists for ordered data, sets for uniqueness.
**Q-HR34**: Design patterns? **A**: Repository, Service Layer, Singleton (model loading), Factory.
**Q-HR35**: Testing approach? **A**: Unit tests for services, integration for APIs.
**Q-HR36**: Code review pet peeve? **A**: Unclear variable names and missing error handling.
**Q-HR37**: Favorite tool? **A**: VS Code with Python + TypeScript extensions.
**Q-HR38**: Version control? **A**: Git with feature branches and squash merges.
**Q-HR39**: Documentation? **A**: I write clear docstrings and maintain README.
**Q-HR40**: What makes code "good"? **A**: Readable, tested, handles errors, and easy to change.
**Q-HR41**: Agile or Waterfall? **A**: Agile — iterative delivery with feedback loops.
**Q-HR42**: Microservices vs Monolith? **A**: Start monolith, split when necessary.
**Q-HR43**: TDD? **A**: I write tests but don't strictly TDD — I test core logic.
**Q-HR44**: First thing on Monday? **A**: Review priorities and any PRs/comments from Friday.
**Q-HR45**: End of day routine? **A**: Commit changes, update task tracker, plan next day.
**Q-HR46**: Proudest achievement? **A**: Building a full-stack AI app that actually works end-to-end.
**Q-HR47**: What do you do outside coding? **A**: [Your actual hobby — chess, reading, sports, etc.]
**Q-HR48**: How do you debug? **A**: Reproduce -> isolate -> log -> fix -> verify.
**Q-HR49**: Favorite programming language? **A**: Python for ML/backend, TypeScript for frontend.
**Q-HR50**: Any final message? **A**: "I'm genuinely excited about this opportunity and would love to contribute to [Company]'s mission."

---

# Section 15 — Project Defense

> Interviewers will challenge your decisions. Be ready to defend trade-offs.

## "Why not use TensorFlow/PyTorch?"
**Defense**: For 15 diseases with 31 binary features, a neural network is overkill. scikit-learn's Decision Tree and Random Forest are more interpretable, faster to train, and need less data. Neural nets would need thousands more samples to outperform RF on this task. We chose the right tool for the problem scale.

## "Your data is synthetic. How do you know it works?"
**Defense**: You're right — synthetic data is a limitation. We've been transparent about this. The models do learn the rules they were trained on (accuracy ~95-98% on test split). Real-world validation would need medical partnership, but the pipeline architecture is production-ready — swap the training data and retrain.

## "Why no real-time streaming?"
**Defense**: Gemini's streaming requires websockets or SSE (Server-Sent Events). We chose simple request-response for V1. Streaming would improve UX for chat, and we'd add it in a future iteration. The architecture supports it — LangChain supports streaming natively.

## "Why in-memory data for doctors/hospitals?"
**Defense**: Speed of development — in-memory data let us build the feature without schema design. For production, these would be MongoDB collections. The code is structured to make this migration trivial: a repository pattern that swaps in-memory dicts for MongoDB queries.

## "Only 15 diseases?"
**Defense**: The 15 diseases represent common categories. The architecture scales to any number — retrain with a larger dataset. The 31-symptom feature set was designed for extensibility, and the ensemble pipeline handles N classes without code changes.

## "How do you prevent prompt injection?"
**Defense**: RAG adds context from trusted medical documents, limiting the utility of injected instructions. The system prompt explicitly instructs Gemini to respond based only on provided medical context. Rate limiting prevents automated abuse. Medical disclaimer warns users. For production, we'd add input sanitization and content filtering.

## "Is this project production-ready?"
**Defense**: The code is production-ready in terms of architecture — async, typed, tested, validated, containerized. The *data* is not production-ready — it needs real medical data and regulatory approval (HIPAA, FDA). Technically, the deployment works. Medically, it's an educational demo.

---

# Section 16 — Common Mistakes

## Architecture Mistakes
- **Blocking the event loop**: Running synchronous ML/SHAP code on the main async thread. Fix: Use `loop.run_in_executor()`.
- **No connection pooling**: Creating a new MongoDB client per request. Fix: Singleton client initialized at startup.
- **CORS misconfiguration**: Allowing all origins (`*`) in production. Fix: Restrict to frontend URL.
- **No rate limiting on AI endpoints**: Gemini costs money. Unprotected endpoints can run up bills. Fix: slowapi with tighter limits on chat routes.

## ML Mistakes
- **Data leakage**: Including target information in features. Fix: Careful train/test split before any preprocessing.
- **Overfitting to synthetic patterns**: The synthetic data has perfect patterns → models show >95% accuracy. Real data would be noisier. Fix: Add noise to synthetic data during training.
- **Not normalizing predictions**: Three models with different probability distributions. Fix: Average probabilities (not raw scores).

## Frontend Mistakes
- **No loading/error states**: Users stare at blank screens. Fix: TanStack Query's isLoading, isError states.
- **Not handling stale JWT**: 401 on expired token. Fix: Clerk's middleware auto-refreshes.
- **Missing form validation**: Users submit empty forms. Fix: Zod schemas with error messages.
- **No responsive design**: Looks broken on mobile. Fix: Tailwind responsive classes.

## Deployment Mistakes
- **Hardcoded environment variables**: Committing secrets to git. Fix: .env.example files only.
- **No Docker health checks**: Container runs but app is broken. Fix: HEALTHCHECK with /api/v1/health.
- **Missing volume mounts**: ChromaDB data lost on container restart. Fix: Docker volumes for persistent data.

---

# Section 17 — Cheat Sheet

## 30-Second Pitch

> "SymptomScope AI is a full-stack health app where users enter symptoms, and an ensemble of ML models predicts diseases with SHAP explanations, while a LangChain/Gemini chatbot answers medical questions using RAG over medical documents."

## Key Numbers

| Metric | Value |
|--------|-------|
| API endpoints | 31 |
| Service modules | 18 |
| Route modules | 10 |
| Frontend pages | 10 |
| ML models | 3 (DT + RF + NB) |
| Diseases | 15 |
| Symptom features | 31 (binary) |
| Training samples | ~3,100 (synthetic) |
| MongoDB collections | 7 |
| Zustand stores | 5 |
| Docker containers | 3 |
| LLM model | Gemini 2.5 Flash |
| RAG chunks | 500 chars, 50 overlap |
| RAG top-k | 5 |

## Quick Architecture

```
Next.js 15 -> FastAPI -> Ensemble (DT+RF+NB) -> SHAP -> Gemini+RAG -> MongoDB
```

## Key Files Reference

| Concept | File |
|---------|------|
| Ensemble prediction | `backend/services/prediction_service.py:51` |
| SHAP explainability | `backend/services/explainability_service.py` |
| LangChain + Gemini | `backend/services/llm_service.py` |
| ChromaDB RAG | `backend/services/rag_service.py` |
| Analytics (527 lines) | `backend/services/analytics_service.py` |
| Model training | `backend/ml/training/train_models.py` |
| Feature encoding | `backend/services/prediction_service.py` |
| Emergency detection | `backend/services/emergency_service.py` |
| JWT auth | `backend/auth/dependency.py` |
| FastAPI entry | `backend/main.py` |
| Frontend middleware | `frontend/src/middleware.ts` |
| Docker compose | `docker-compose.yml` |
| CI/CD | `.github/workflows/ci.yml` |

## Common Interview Keywords

| Keyword | How It Applies |
|---------|---------------|
| **Async/Await** | FastAPI + Motor (async MongoDB) |
| **Dependency Injection** | Repository -> Service -> Router (FastAPI Depends) |
| **Repository Pattern** | Data access abstraction over MongoDB |
| **Ensemble Learning** | Averaging 3 models for better predictions |
| **SHAP** | Game-theoretic feature attribution |
| **RAG** | Retrieval-Augmented Generation for grounded LLM responses |
| **Vector Embeddings** | Google embedding-001 for ChromaDB search |
| **Server State** | TanStack Query managing cached API data |
| **Client State** | Zustand for UI state (5 stores) |
| **JWT** | RS256 tokens from Clerk for stateless auth |
| **CI/CD** | GitHub Actions lint + test on push |
| **Multi-stage Build** | Docker build optimization ~150MB final image |
| **Rate Limiting** | slowapi, 60/min general, 20/min chat |

---

# Section 18 — Glossary

| Term | Definition |
|------|-----------|
| **Ensemble** | Combining multiple ML models for better accuracy |
| **SHAP** | SHapley Additive exPlanations — explains each feature's contribution |
| **RAG** | Retrieval-Augmented Generation — adds document context to LLM calls |
| **ChromaDB** | Open-source vector database for embedding similarity search |
| **LangChain** | Framework for building LLM-powered applications |
| **Gemini** | Google's multimodal AI model (flash = fast, cheap) |
| **JWT** | JSON Web Token — stateless auth token |
| **JWKS** | JSON Web Key Set — public keys for verifying JWTs |
| **Clerk** | User management + authentication SaaS |
| **Motor** | Async MongoDB driver for Python |
| **Pydantic** | Python data validation via type hints |
| **TanStack Query** | Server state management for React |
| **Zustand** | Lightweight (~1KB) client state management |
| **Recharts** | React charting library (used in dashboard) |
| **FPDF** | Python library for PDF generation |
| **RS256** | RSA with SHA-256 — asymmetric JWT signing algorithm |
| **SSR** | Server-Side Rendering |
| **TTR** | Time-to-Response (for analytics caching) |
| **SHAP Values** | Feature contributions that sum to the prediction |
| **predict_proba()** | Returns probability for each class |
| **StreamingResponse** | FastAPI response type for file downloads |
| **slowapi** | Python rate limiting library for FastAPI |
| **shadcn/ui** | Copy-paste React component library |
| **Zod** | TypeScript-first schema validation |
| **standalone** | Next.js output mode optimized for Docker |
| **YAGNI** | You Aren't Gonna Need It — don't over-engineer |
| **DRY** | Don't Repeat Yourself |
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **FHIR** | Fast Healthcare Interoperability Resources (health data standard) |

---

# Section 19 — Self-Study Roadmap

## Week 1-2: Fundamentals
- [ ] Review Python (async/await, type hints, classes)
- [ ] Review FastAPI docs (routers, dependencies, Pydantic)
- [ ] Review MongoDB basics (documents, collections, indexes)
- [ ] Run SymptomScope AI locally (docker-compose up)

## Week 3-4: ML Deep Dive
- [ ] Study scikit-learn: DecisionTree, RandomForest, NaiveBayes
- [ ] Understand predict() vs predict_proba()
- [ ] Read SHAP documentation and TreeExplainer
- [ ] Run train_models.py and understand the synthetic data generation
- [ ] Experiment: add a new disease to the registry and retrain

## Week 5-6: AI/GenAI
- [ ] Study LangChain basics (LLMs, Prompts, Chains)
- [ ] Read about RAG architecture and ChromaDB
- [ ] Experiment: test prompts in ml/prompts/
- [ ] Study embedding models and vector similarity search
- [ ] Try: swap Gemini for OpenAI (change one line in settings.py)

## Week 7-8: System Design
- [ ] Read about microservices vs monoliths
- [ ] Study caching strategies (in-memory, Redis, CDN)
- [ ] Understand Docker multi-stage builds
- [ ] Practice: diagram the full request flow on a whiteboard
- [ ] Scale discussion: how would you handle 100K users?

## Week 9-10: Behavioral Preparation
- [ ] Practice answers for Section 13 (100+ technical questions)
- [ ] Practice answers for Section 14 (50+ HR questions)
- [ ] Do mock interviews (Section 20)
- [ ] Review common mistakes (Section 16)

## Resources
- **FastAPI**: fastapi.tiangolo.com
- **scikit-learn**: scikit-learn.org/stable/documentation
- **SHAP**: shap.readthedocs.io
- **LangChain**: python.langchain.com/docs
- **ChromaDB**: docs.trychroma.com
- **Next.js 15**: nextjs.org/docs
- **MongoDB**: mongodb.com/docs

---

# Section 20 — Mock Interview

## Round 1: Technical (45 min)

**Interviewer**: "Walk me through your project."
**You**: [Use 30-second pitch from Section 17, then dive deeper]

**Interviewer**: "Why MongoDB over PostgreSQL?"
**You**: "For this project, prediction data is naturally JSON-like with nested structures (symptoms array, predictions array with objects). MongoDB's document model stores this without joins. The schema evolves as we add features — no migrations needed. Trade-off: no ACID across collections, but our app doesn't need cross-document transactions."

**Interviewer**: "How does your ensemble work exactly?"
**You**: "Three models each call predict_proba() returning 15 probabilities. We average with np.mean(axis=0) to get ensemble probabilities. Top 3 by average probability are the predictions. The highest probability * 100 = confidence score."

**Interviewer**: "What's the time complexity of a prediction?"
**You**: "Feature encoding: O(n) where n=31 symptoms. Each model: O(log depth) for DecisionTree, O(trees * log depth) for RandomForest (~100 trees), O(classes * features) for NaiveBayes. SHAP: O(2^features * model_eval) on background data. Total: ~50-100ms per prediction including SHAP."

**Interviewer**: "How would you handle 100 concurrent users?"
**You**: "FastAPI is async — it handles concurrency without threading overhead. MongoDB via Motor is non-blocking. The main bottleneck would be the Gemini API. Solutions: (1) Rate limit chat endpoints to 20/min per user. (2) Cache common chat responses. (3) For predictions, results are deterministic — cache identical symptom sets."

## Round 2: System Design (45 min)

**Problem**: "Design a system that scales this to 1M users."

**Storage**: MongoDB Atlas with sharding on user_id. Redis cache for predictions and analytics. ChromaDB moved to a separate service with replication.

**Computation**: Prediction service behind a load balancer — horizontal scaling. ML models loaded in each instance (small, ~50MB total). For heavy analytics, use Celery workers with Redis as broker.

**AI**: Gemini API calls are the bottleneck. Add response caching (identical questions → cached answer). Implement request queue with priority (predictions > chat).

**Frontend**: Vercel's Edge Network for CDN caching. Static pages pre-rendered. P95 response target: <500ms for predictions, <2s for chat (including Gemini).

## Round 3: Behavioral (30 min)

**Interviewer**: "Tell me about a time you had a technical disagreement."
**You**: "During design, a teammate wanted to use raw Gemini API without LangChain. I argued LangChain provides prompt management, easy model swapping, and RAG support out of the box. We compromised: I prototyped with LangChain in 2 hours, showed the advantage, and we went with LangChain."

**Interviewer**: "What was the hardest bug you fixed?"
**You**: "SHAP blocked the async event loop and crashed the server. I was using TreeExplainer directly in an async route. The fix: use `asyncio.get_event_loop().run_in_executor(None, explainer.shap_values, data)`. This runs the synchronous SHAP code in a thread pool without blocking the event loop."

**Interviewer**: "What would you do differently?"
**You**: "(1) Real data instead of synthetic from day one. (2) Streaming for chat responses. (3) MongoDB for doctors/hospitals instead of in-memory. (4) Add tests earlier — we have unit tests but could use more integration tests."

---

> **Good luck with your interviews! Remember:**
> - Know your codebase — read the actual files mentioned in this guide
> - Practice talking about trade-offs, not just features
> - Use STAR (Situation, Task, Action, Result) for behavioral questions
> - Show enthusiasm for building and learning
> - Be honest about limitations — then explain how you'd fix them


