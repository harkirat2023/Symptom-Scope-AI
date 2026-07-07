## **TECHSTACK.md** 

## **SymptomScope AI** 

## **Recommended Tech Stack (2026)** 

Version: 1.0 

## **Philosophy** 

SymptomScope AI is not simply a CRUD MERN application. 

The platform contains: 

- Machine Learning inference 

- Healthcare data 

- 

- Analytics dashboards 

- Authentication 

- Real-time recommendations 

- Explainable AI 

- Future API integrations 

The technology choices should optimize for: 

✓ Developer Productivity 

✓ Scalability 

✓ Performance 

- ✓ AI/ML Compatibility 

- ✓ Startup-Grade Architecture 

- ✓ Resume Impact 

## **Final Recommended Stack** 

|Layer|Technology|
|---|---|
|Frontend|Next.js 16 + TypeScript|
|UI|Tailwind CSS v4 + shadcn/ui|



1 

|Layer|Technology|
|---|---|
|State Management|TanStack Query + Zustand|
|Backend API|FastAPI|
|ML Engine|Scikit-Learn|
|Authentication|Clerk|
|Database|MongoDB Atlas|
|File Storage|Cloudinary|
|Charts|Recharts|
|Background Jobs|Upstash QStash|
|Deployment|Vercel + Railway|
|Monitoring|Sentry|
|Analytics|PostHog|



## **Frontend** 

## **Recommendation** 

Next.js 16 

## **Why?** 

Compared to React SPA: 

Advantages: 

- Better SEO 

- Better performance 

- Server Components 

- Built-in routing 

- Streaming UI • Production-ready architecture 

Healthcare products benefit heavily from: 

- Fast load times • High trust 

- Excellent accessibility 

2 

## **Frontend Stack** 

```
Next.js 16
TypeScript
Tailwind CSS v4
shadcn/ui
TanStack Query
Zustand
Framer Motion
```

## **UI Library** 

## **Recommendation** 

shadcn/ui 

## **Why?** 

For healthcare dashboards: 

- Modern SaaS look 

- Highly customizable 

- Accessibility built-in 

- Works perfectly with Tailwind 

Alternative: 

Material UI 

Reason rejected: 

- Looks generic 

- Harder to create premium healthcare feel 

## **Styling** 

## **Recommendation** 

Tailwind CSS v4 

3 

## **Why?** 

Benefits: 

- Faster development 

- Design system consistency 

- Small bundle size 

- Excellent with shadcn 

## **State Management** 

## **Recommendation** 

TanStack Query + Zustand 

## **TanStack Query** 

Used for: 

- API calls 

- Caching 

- Retries 

- Background updates 

## **Zustand** 

Used for: 

- Auth state 

- Dashboard preferences 

- Temporary symptom selections 

Why not Redux? 

- Overkill • More boilerplate 

- Worse developer experience 

## **Backend** 

## **Recommendation** 

FastAPI 

4 

## **Why FastAPI over Flask?** 

Your project already uses: 

- Python 

- Scikit-Learn 

- Pandas 

- NumPy 

FastAPI offers: 

- Better performance 

- Async support 

- Automatic Swagger Docs 

- Type Safety 

- Production-grade APIs 

Performance Comparison: 

Flask ≈ Good 

FastAPI ≈ Excellent 

## **Backend Stack** 

```
FastAPI
Pydantic
Uvicorn
Python 3.13
```

## **Machine Learning Layer** 

## **Recommendation** 

Scikit-Learn 

## **Models** 

Decision Tree 

Random Forest 

5 

## **Supporting Libraries** 

```
Scikit-Learn
Pandas
NumPy
Joblib
SHAP
```

## **Why SHAP?** 

Your PRD requires: 

Feature Importance Analysis 

Explainable Predictions 

Example: 

Prediction: Influenza 

Contributing Symptoms: 

- Fever • Cough • Fatigue 

SHAP provides transparent AI explanations. 

## **Authentication** 

## **Recommendation** 

Clerk 

## **Why?** 

Benefits: 

- Email login 

- Google login 

- OTP support 

- User management 

- Session handling 

Implementation time: 

6 

1 hour 

Compared to JWT: 

Several days 

## **Alternative** 

Auth.js 

Use only if: 

• Full self-hosting required 

## **Database** 

## **Recommendation** 

MongoDB Atlas 

## **Why?** 

Your PRD stores: 

- User profiles 

- Symptom arrays 

- Prediction logs 

- Medical history 

- Doctor recommendations 

All are semi-structured documents. 

MongoDB fits naturally. 

## **Collections** 

```
users
predictions
reports
symptom_logs
doctors
hospitals
alerts
```

7 

## **Search Layer** 

## **Recommendation** 

MongoDB Atlas Search 

## **Why?** 

Needed for: 

- Symptom search 

- Doctor search 

- Hospital search 

Avoid Elasticsearch initially. 

## **Doctor Recommendation System** 

## **Phase 1** 

Static curated database 

Example: 

Punjab 

Ludhiana 

Amritsar 

Patiala 

Jalandhar 

## **Phase 2** 

Google Maps Integration 

Features: 

- Nearby hospitals 

- Ratings 

- Distance 

- Directions 

8 

## **File Storage** 

## **Recommendation** 

Cloudinary 

## **Used For** 

- Medical reports 

- Exported PDFs 

- User documents 

## **Charts & Analytics** 

## **Recommendation** 

Recharts 

## **Used For** 

- Symptom trends 

- Severity trends 

- Health timeline 

- Disease frequency 

Why? 

- Lightweight • Beautiful 

- React-native support 

## **Notifications** 

## **Recommendation** 

Novu 

## **Used For** 

- Emergency alerts 

- Severe disease notifications 

- Report generation updates 

9 

## **Monitoring** 

## **Recommendation** 

Sentry 

## **Tracks** 

- Backend crashes 

- API failures 

- ML inference errors 

- Frontend exceptions 

Critical for healthcare applications. 

## **Analytics** 

## **Recommendation** 

PostHog 

## **Track** 

- User retention 

- Prediction completion rate 

- Most searched symptoms 

- Conversion metrics 

## **Deployment** 

## **Frontend** 

## **Vercel** 

Benefits: 

- Best Next.js support 

- Automatic deployments 

- Edge optimization 

10 

## **Backend** 

## **Railway** 

Benefits: 

- FastAPI support 

- Docker support 

- Easy scaling 

- Simple setup 

Alternative: 

Render 

## **Database** 

## **MongoDB Atlas** 

Benefits: 

- Managed infrastructure 

- Backups 

- Search capabilities 

## **CI/CD** 

## **GitHub Actions** 

Pipeline: 

```
Push Code
     ↓
Run Tests
     ↓
Build Application
     ↓
Deploy Automatically
```

11 

## **Security** 

## **Requirements** 

- HTTPS Everywhere 

- Clerk Authentication 

- Rate Limiting 

- Input Validation 

- Passwordless Login 

- Encrypted Secrets 

- MongoDB Network Rules 

## **Architecture Overview** 

**==> picture [440 x 378] intentionally omitted <==**

**----- Start of picture text -----**<br>
┌──────────────────────────┐<br>│       Next.js 16         │<br>│      Frontend UI         │<br>└────────────┬─────────────┘<br>             │<br>             ▼<br>┌──────────────────────────┐<br>│        FastAPI           │<br>│      REST API Layer      │<br>└────────────┬─────────────┘<br>             │<br>    ┌────────┴────────┐<br>    ▼                 ▼<br>ML Engine         MongoDB Atlas<br>(Scikit-Learn)     Users<br>                   Predictions<br>                   Reports<br>                   Doctors<br>    ▼<br>SHAP Explainability<br>    ▼<br>Prediction Results<br>**----- End of picture text -----**<br>


12 

## **Why This Stack Is Best For Placements** 

This stack demonstrates: 

- Modern Frontend Engineering 

- Production Backend Development 

- Machine Learning Deployment 

- Explainable AI 

- Authentication 

- Cloud Deployment 

- Healthcare SaaS Architecture 

Recruiters will immediately recognize experience in: 

- Next.js 

- FastAPI 

- MongoDB 

- Scikit-Learn 

- Cloud Infrastructure 

which is significantly stronger than a traditional React + Flask academic project. 

## **Final Recommendation** 

Frontend: Next.js 16 + TypeScript + Tailwind + shadcn/ui 

Backend: FastAPI + Pydantic + Uvicorn 

ML: Scikit-Learn + SHAP + Joblib 

Auth: Clerk 

Database: MongoDB Atlas 

Deployment: Vercel + Railway 

Monitoring: Sentry 

Analytics: PostHog 

This provides the best balance of development speed, scalability, portfolio value, and placement impact for SymptomScope AI in 2026. 

13 

