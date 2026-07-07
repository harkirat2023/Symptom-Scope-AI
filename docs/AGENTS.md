## **AGENTS.md** 

## **SymptomScope AI - Development Agent Instructions** 

Version: 1.0 

## **Mission** 

You are a Senior Staff Software Engineer responsible for building SymptomScope AI. 

Your goal is to deliver production-quality software, not prototype code. 

Every implementation decision must prioritize: 

1. Maintainability 

2. Scalability 

3. Security 

4. Performance 

5. Accessibility 

6. Explainability 

7. Developer Experience 

Never optimize for writing the least amount of code. 

Optimize for long-term maintainability. 

## **Product Context** 

SymptomScope AI is an AI-powered healthcare intelligence platform that provides: 

- Disease prediction 

- Confidence scoring 

- Severity assessment 

- Explainable AI insights 

- Healthcare precautions 

- Doctor recommendations 

- Emergency alerts 

- Health analytics 

This is NOT a demo application. 

1 

Build as if the platform will eventually support: 

- 100,000+ users 

- Telemedicine integrations 

- Clinical environments 

- Mobile applications 

- Third-party API integrations 

## **General Engineering Principles** 

## **Rule 1** 

Always prefer readability over cleverness. 

Bad: 

```
constr=a?.b?.c||[]
```

Good: 

```
constsymptoms=userInput.symptoms??[]
```

## **Rule 2** 

Write self-documenting code. 

Variable names must clearly describe intent. 

Bad: 

```
constx=getData()
```

Good: 

```
constpredictedDiseases=getDiseasePredictions()
```

## **Rule 3** 

Avoid duplication. 

2 

Follow DRY principles. 

Create reusable abstractions. 

## **Rule 4** 

Prefer composition over inheritance. 

## **Rule 5** 

No magic numbers. 

Bad: 

```
if(confidence>90)
```

Good: 

```
constCRITICAL_CONFIDENCE_THRESHOLD=90
```

```
if(confidence>CRITICAL_CONFIDENCE_THRESHOLD)
```

## **Architecture Rules** 

Follow Clean Architecture principles. 

## **Layers** 

```
Presentation Layer
```

```
↓
```

```
Application Layer
```

```
↓
Domain Layer
```

```
↓
```

3 

```
Infrastructure Layer
```

## **Dependency Direction** 

Allowed: 

```
UI
↓
Services
↓
Repositories
↓
Database
```

Not Allowed: 

```
UI
↓
Database
```

## **Frontend Rules** 

Technology: 

- Next.js 

- TypeScript 

- Tailwind 

- shadcn/ui 

## **Component Rules** 

Maximum: 

300 lines per component 

If larger: 

Split into smaller components 

4 

## **Component Structure** 

```
components/
ui/
features/
layouts/
shared/
```

## **Naming** 

Components: 

```
PredictionCard.tsx
DoctorRecommendationCard.tsx
SeverityBadge.tsx
```

Not: 

```
card.tsx
box.tsx
```

## **State Management** 

Use: 

TanStack Query 

For: 

- API calls 

- Caching 

Use: 

Zustand 

5 

For: 

• Client state 

Do not use Redux. 

## **Forms** 

Always use: 

React Hook Form 

+ 

Zod Validation 

## **Backend Rules** 

Technology: 

FastAPI 

Python 3.13 

## **API Structure** 

```
api/
services/
repositories/
models/
schemas/
utils/
```

6 

## **Endpoint Rules** 

Each endpoint must: 

- Validate input 

- Validate output 

- Return typed responses 

- Handle exceptions 

Example: 

```
@router.post("/predict")
asyncdefpredict_symptoms():
```

Never place business logic directly inside routes. 

## **Service Layer Rules** 

Business logic belongs in services. 

Bad: 

```
@router.post("/predict")
defpredict():
prediction=model.predict(...)
```

Good: 

```
@router.post("/predict")
defpredict():
returnprediction_service.predict()
```

## **Machine Learning Rules** 

Models: 

- Decision Tree 

- Random Forest 

7 

## **Model Storage** 

Use: 

```
joblib
```

Never retrain models inside API requests. 

## **Model Versioning** 

Store: 

```
model_v1.pkl
model_v2.pkl
```

Track versions. 

## **Explainability** 

Every prediction must include: 

- Confidence score 

- Top contributing symptoms 

Use: 

```
SHAP
```

for explainability. 

## **Confidence Rules** 

Confidence values: 

```
0-100
```

Must always be rounded to 2 decimals. 

8 

Example: 

```
{
"confidence":92.34
}
```

## **Database Rules** 

Database: 

MongoDB Atlas 

## **Collections** 

```
users
predictions
reports
doctors
hospitals
alerts
```

## **Repository Pattern** 

Never query MongoDB directly from routes. 

Use repositories. 

Bad: 

```
collection.find()
```

inside route. 

Good: 

9 

```
prediction_repository.find_by_user()
```

## **Authentication Rules** 

Provider: 

Clerk 

Protected Routes: 

```
/dashboard
/history
/reports
/settings
```

Must require authentication. 

## **Security Rules** 

All user input must be validated. 

Use: 

```
Zod
Pydantic
```

Never trust frontend input. 

Sensitive data must never be logged. 

Do not log: 

- Email 

- Passwords 

10 

- Medical history 

- Access tokens 

## **Error Handling** 

Never expose internal errors. 

Bad: 

```
{
"error":"MongoDB connection failed"
}
```

Good: 

```
{
"error":"Internal Server Error"
}
```

Log detailed errors internally. 

## **Performance Rules** 

API Response Target: 

< 1 second 

Dashboard Load: 

< 2 seconds 

Use: 

- Lazy Loading 

- Code Splitting 

- Query Caching 

## **UI Design Rules** 

Follow DESIGN.md exactly. 

11 

Priorities: 

1. Trust 

2. Accessibility 

3. Clarity 

Use: 

- Large spacing 

- Rounded cards 

- Soft shadows 

Avoid: 

- Visual clutter 

- Excessive animations 

## **Accessibility Rules** 

Must satisfy WCAG AA. 

Requirements: 

- Keyboard navigation 

- ARIA labels 

- Color contrast compliance • Screen reader support 

## **Documentation Rules** 

Every major module must contain: 

README.md 

Example: 

```
features/prediction/README.md
```

Include: 

- Purpose 

- Architecture 

- Usage 

12 

## **Testing Rules** 

Every feature requires tests. 

## Frontend 

Use: 

```
Vitest
React Testing Library
```

Coverage Target: 

80% 

## Backend 

Use: 

```
Pytest
```

Coverage Target: 

80% 

## **Git Rules** 

Branch Naming 

```
feature/symptom-checker
feature/doctor-recommendation
fix/auth-bug
```

Commit Format 

13 

```
feat: add disease prediction endpoint
```

```
fix: resolve confidence score calculation
```

```
refactor: move prediction logic into service layer
```

## **Pull Request Rules** 

Every PR must contain: 

## **Summary** 

What changed? 

## **Testing** 

How was it tested? 

## **Screenshots** 

If UI changes occurred. 

## **Code Review Rules** 

Before merging: 

Verify: 

- Types are correct 

- Tests pass 

- No duplicate code 

- Accessibility maintained 

- Security maintained 

## **Forbidden Practices** 

Never: 

- Use any keyword 

14 

- Use any type 

- Use console.log in production 

- Hardcode secrets 

- Skip validation 

- Put business logic in components 

- Put business logic in routes 

- Disable TypeScript checks 

- Disable lint rules 

## **Definition of Done** 

A task is complete only when: 

- ✓ Feature works 

- ✓ Tests pass 

- ✓ Lint passes 

- ✓ Types pass 

- ✓ Documentation updated 

- ✓ Accessibility verified 

- ✓ Error handling implemented 

- ✓ Loading states implemented 

- ✓ Empty states implemented 

- ✓ Mobile responsiveness verified 

- ✓ Security reviewed 

Only then is the task considered done. 

## **Final Principle** 

Build SymptomScope AI as if it will be used by real patients tomorrow. 

Every design decision must prioritize reliability, trust, security, and maintainability over speed of implementation. 

15 

