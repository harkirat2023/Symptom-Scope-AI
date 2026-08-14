# SymptomScope AI — TECHSTACK.md

## 1. Purpose

This is the **minimal canonical technology stack** for SymptomScope AI. The existing architecture remains unchanged. The only addition is disease- and location-aware doctor/hospital recommendation.

**Do not replace working technologies or introduce unnecessary technologies.**

## 2. Frontend

| Technology | Purpose |
|---|---|
| Next.js 15.5.19 | Frontend framework and routing |
| React | UI components |
| TypeScript | Type safety |
| Tailwind CSS | Styling and responsive design |
| shadcn/ui | Reusable UI components |

Responsibilities:
- Authentication-aware UI
- Dashboard
- Symptom Checker
- Prediction Results
- Recovery Plan
- AI Health Assistant
- Doctor/Hospital recommendations
- History
- Reports
- Reminders
- Find Care
- Settings

## 3. Backend

| Technology | Purpose |
|---|---|
| Python | Backend and ML |
| FastAPI | REST API |
| Pydantic | Validation |

Responsibilities:
- REST APIs
- Authentication verification
- Business logic
- ML inference
- AI/RAG integration
- Doctor/hospital recommendation logic
- Recovery plans
- Medical recommendations
- History
- Reports
- Reminders

Routes remain thin; business logic belongs in services/use cases.

## 4. Database

| Technology | Purpose |
|---|---|
| MongoDB | Persistent application data |

Used for existing application data including prediction history, medical metadata, provider information, recovery plans, reminders and reports.

## 5. Authentication

| Technology | Purpose |
|---|---|
| Clerk | Authentication |
| JWT | Authenticated API requests |

Clerk remains the authentication source of truth. Do not create another authentication system.

# 6. Layer 1 — ML Disease Prediction

| Technology | Purpose |
|---|---|
| Pandas | Dataset loading/preprocessing |
| NumPy | Numerical processing |
| Scikit-learn | ML models/evaluation |
| Joblib | Model serialization |
| SHAP | Explainability |

### Models

- Decision Tree
- Random Forest
- Naive Bayes

### Dataset

The primary training source is the approved **Kaggle disease-symptom dataset**.

Synthetic data must not be used as the primary production training source.

### Workflow

```text
Kaggle Dataset
 ↓
Pandas / NumPy
 ↓
Preprocessing
 ↓
Feature Encoding
 ↓
ML Training
 ↓
Evaluation
 ↓
Joblib Models
 ↓
FastAPI Inference
 ↓
Disease + Confidence
 ↓
SHAP Explanation
```

**Only this ML layer predicts the disease.**

# 7. Layer 2 — Doctor/Hospital Recommendation

This is an extension of the existing AI functionality.

| Technology | Purpose |
|---|---|
| LangChain | Recommendation orchestration and dynamic prompts |
| Groq | Recommendation generation |
| MongoDB / existing provider data | Doctor/hospital information |
| ChromaDB | Existing medical RAG knowledge where relevant |

### Inputs

```text
Predicted Disease
+
Relevant Specialty
+
User Location
+
Available Doctor/Hospital Data
```

### Workflow

```text
ML Predicted Disease
 ↓
Relevant Specialty
 ↓
User Location
 ↓
Available Provider Data
 ↓
LangChain PromptTemplate
 ↓
Groq
 ↓
Structured Recommendation
```

The LLM does not predict or modify the disease and must not invent provider details.

## 8. Dynamic Prompting

LangChain constructs the recommendation prompt using available:
- Disease.
- Severity where available.
- Specialty.
- User city/location.
- Candidate doctors.
- Candidate hospitals.
- Relevant medical context where required.

Groq should recommend only from supplied provider information.

## 9. Structured Output

The recommendation service should return a predictable schema such as:

```text
predicted_disease
recommended_specialty
location
recommended_doctors
recommended_hospitals
reasons
emergency_warning
disclaimer
```

The exact implementation schema remains defined by backend models.

# 10. Existing AI Assistant / RAG

| Technology | Purpose |
|---|---|
| LangChain | RAG orchestration |
| Groq | AI generation |
| ChromaDB | Vector retrieval |
| RAG | Grounded medical information |

```text
User Question
 ↓
LangChain
 ↓
ChromaDB
 ↓
Relevant Medical Context
 ↓
Groq
 ↓
Grounded Answer
```

This remains separate from disease prediction.

# 11. Recovery Plan

```text
Predicted Disease
+
Verified Medical Knowledge
+
Severity
 ↓
LangChain + Groq
 ↓
Personalized Presentation
```

Groq must not change the disease or prescribe medication.

# 12. Core Features That Must Not Be Disturbed

- Clerk authentication
- Multi-step symptom checker
- Kaggle-trained disease prediction
- Decision Tree
- Random Forest
- Naive Bayes
- Confidence scoring
- SHAP explainability
- Severity classification
- Medical precautions
- Specialist mapping
- Emergency detection
- Doctor/hospital recommendation
- Health dashboard
- Prediction history
- Recovery Plan
- LangChain + Groq AI assistant
- ChromaDB RAG
- PDF/CSV reports
- Daily reminders
- Specific-day reminders
- MongoDB persistence

# 13. Development Tools

| Tool | Purpose |
|---|---|
| Git | Version control |
| GitHub | Repository/collaboration |
| VS Code | Development |
| Postman | API testing |

Use existing project tooling.

# 14. Environment Variables

Secrets must never be hardcoded.

Examples:

```text
MONGODB_URI
Groq_API_KEY
Clerk configuration
API base URL
Other project-specific secrets
```

Maintain `.env.example` without real secrets.

# 15. Architecture

```text
                    USER
                      ↓
              Next.js / React
                      ↓
                  Clerk
                      ↓
                   FastAPI
                      ↓
                Business Logic
                      ↓
          ┌───────────┴───────────┐
          ↓                       ↓
     ML Prediction            AI Services
          ↓                       ↓
 DT + RF + NB              LangChain + Groq
          ↓                       ↓
 Predicted Disease          RAG / Recommendation
          │                       │
          └───────────┬───────────┘
                      ↓
                   MongoDB
```

Two-layer product logic:

```text
Layer 1:
Symptoms → Kaggle-trained ML → Disease

Layer 2:
Disease + Specialty + Location + Provider Data
→ LangChain + Groq
→ Doctor/Hospital Recommendation
```

# 16. Technology Selection Rules

1. Keep the current stack.
2. Do not add another authentication system.
3. Do not add another primary database.
4. Do not replace the three core ML models.
5. Do not use an LLM for disease prediction.
6. Do not replace ChromaDB unnecessarily.
7. Do not add another vector database for this recommendation feature.
8. Keep provider data structured and traceable.
9. Use LangChain for dynamic recommendation orchestration.
10. Use structured output rather than uncontrolled recommendation text.
11. Do not allow Groq to invent provider details.
12. Keep frontend/backend contracts stable.
13. Keep ML, AI and API responsibilities separated.
14. Preserve all existing product workflows.

# 17. Minimal Stack Summary

```text
Frontend
Next.js 15.5.19 + React + TypeScript + Tailwind CSS + shadcn/ui

Backend
Python + FastAPI + Pydantic

Database
MongoDB

Authentication
Clerk + JWT

ML
Pandas + NumPy + Scikit-learn + Joblib + SHAP

ML Models
Decision Tree + Random Forest + Naive Bayes

AI
LangChain + Groq

RAG
ChromaDB

Healthcare Recommendation
LangChain PromptTemplate + Groq + structured provider data

Engineering
Git + GitHub + Postman + VS Code
```

**This remains the canonical minimal technology stack for SymptomScope AI.**
