# SymptomScope AI — Product Requirements Document (PRD)

**Version:** 2.1  
**Product:** SymptomScope AI  
**Type:** AI/ML-Based Symptom Intelligence & Preliminary Health Screening Platform

## 1. Executive Summary

SymptomScope AI is a full-stack symptom intelligence platform for fast, structured and explainable preliminary health screening. It combines supervised ML, curated medical knowledge, explainability, personalized recovery guidance and generative AI.

The user enters symptoms through a guided symptom checker. The ML engine uses the approved Kaggle symptom-disease dataset with Decision Tree, Random Forest and Naive Bayes models to predict a disease and confidence information. SHAP explains important symptom contributions. Existing medical metadata provides severity, precautions, specialist mapping and emergency indicators.

A separate second layer uses the predicted disease and the user's location to provide relevant doctor and hospital suggestions. LangChain builds the recommendation context and Gemini returns structured recommendations. **The AI layer must never replace, modify or independently determine the ML disease prediction.**

**The platform is for preliminary health information and screening, not definitive diagnosis or replacement of healthcare professionals.**

## 2. Product Vision

Help users understand reported symptoms, receive a preliminary ML-based disease prediction, understand the result, obtain relevant health information and find appropriate healthcare providers based on the predicted disease and location.

## 3. Core Goals

1. Provide rapid symptom-to-disease prediction.
2. Train the prediction engine on the approved Kaggle symptom-disease dataset.
3. Provide confidence information without presenting it as certainty.
4. Explain predictions using SHAP.
5. Provide severity, precautions and specialist guidance.
6. Detect configured emergency conditions.
7. Recommend relevant doctors and hospitals based on disease and user location.
8. Provide a grounded LangChain + Gemini health assistant.
9. Generate structured recovery guidance.
10. Maintain history, reports and reminders.
11. Preserve secure authentication and user data.

## 4. Non-Goals

The system must not:
- Claim to provide definitive diagnosis.
- Replace healthcare professionals.
- Prescribe medication or dosage.
- Allow an LLM to change the ML prediction.
- Allow an LLM to independently diagnose.
- Invent doctors, hospitals, addresses, phone numbers or availability.

## 5. Core User Flow

```text
User
 ↓
Clerk Authentication
 ↓
Symptom Checker
 ↓
Validation
 ↓
Kaggle-Trained ML Engine
 ↓
Decision Tree + Random Forest + Naive Bayes
 ↓
Disease + Confidence
 ↓
SHAP Explanation
 ↓
Severity + Medical Metadata
 ↓
Disease → Relevant Specialty
 ↓
User Location
 ↓
Doctor/Hospital Recommendation Layer
 ↓
Results
 ↓
Recovery Plan / AI Assistant / Reports
 ↓
History
```

# 6. Layer 1 — Disease Prediction

### Symptom Checker

Users can:
- Search symptoms.
- Select symptoms.
- Review/remove symptoms.
- Submit an assessment.

### ML Prediction

The prediction engine uses:
- Decision Tree.
- Random Forest.
- Naive Bayes.

It returns, where implemented:
- Predicted disease.
- Top predictions.
- Confidence/probability information.
- SHAP explanation.

**Architecture rule:** the ML layer is the only disease-prediction layer. LangChain/Gemini must not replace, override or modify the predicted disease.

# 7. Dataset and ML Pipeline

The primary training source is the approved **Kaggle disease-symptom dataset**.

**Synthetic data must not be used as the primary production training source.**

```text
Kaggle Dataset
 ↓
Validation
 ↓
Cleaning / Normalization
 ↓
Feature Encoding
 ↓
Train/Test Split
 ↓
Decision Tree + Random Forest + Naive Bayes
 ↓
Evaluation
 ↓
Model Serialization
 ↓
FastAPI Inference
```

Required metrics:
- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

The previously referenced ~89% accuracy should only be reported if reproduced on the validated evaluation dataset with documented methodology.

# 8. Explainability

SHAP shall explain important symptom contributions where supported.

The user should understand:
- Which symptoms contributed most.
- How symptoms influenced the prediction.
- Why the result is not medical certainty.

# 9. Severity and Medical Metadata

Each supported disease should have configured:
- Severity.
- Precautions.
- Relevant specialist.
- Emergency indicators where applicable.

These mappings come from configured medical data/rules, not dynamically invented by Gemini.

# 10. Layer 2 — Doctor and Hospital Recommendation

### Objective

After the ML engine predicts a disease, the system recommends relevant healthcare providers using:
1. Predicted disease.
2. Relevant medical specialty.
3. User location.
4. Available provider information.

### Flow

```text
Predicted Disease
      +
Disease Metadata
      +
User Location
      ↓
Relevant Specialty
      ↓
Available Doctors / Hospitals
      ↓
LangChain PromptTemplate
      ↓
Gemini
      ↓
Structured Recommendation
      ↓
User
```

### Dynamic Prompt

LangChain shall construct the recommendation prompt using available context such as:
- Predicted disease.
- Severity where available.
- Relevant specialty.
- User city/location.
- Available doctor information.
- Available hospital information.
- Relevant medical knowledge where required.

The prompt must instruct the LLM to recommend only from supplied provider information.

### Structured Output

The recommendation should use a predictable schema such as:

```text
predicted_disease
recommended_specialty
location
recommended_doctors[]
recommended_hospitals[]
reasons[]
emergency_warning
disclaimer
```

The exact schema must follow the implementation.

### Safety

The LLM must not:
- Change the predicted disease.
- Create a new diagnosis.
- Invent providers or provider details.
- Claim a provider is medically superior without supporting data.
- Replace emergency services.

The recommendation layer is an information/matching layer, not a clinical decision-maker.

# 11. User Location

The user should provide a city/location when healthcare recommendations are requested.

Example:

```text
Predicted Disease: Asthma
User Location: Patiala
 ↓
Configured Relevant Specialty
 ↓
Available Local Providers
 ↓
LangChain + Gemini
 ↓
Relevant Recommendations
```

Location must not affect disease prediction.

# 12. AI Health Assistant

The existing AI assistant remains separate from disease prediction.

Technology:
- LangChain.
- Gemini.
- ChromaDB.
- RAG.

```text
User Question
 ↓
LangChain
 ↓
ChromaDB Retrieval
 ↓
Curated Medical Context
 ↓
Gemini
 ↓
Grounded Response
```

It may explain the predicted condition, general medical concepts, precautions and recovery information. It must not alter the prediction.

# 13. Recovery Plan

The existing Recovery Plan remains:

```text
Predicted Disease
+
Severity
+
Verified Medical Knowledge
 ↓
LangChain + Gemini
 ↓
Personalized Presentation
```

Gemini must not prescribe medication or override verified medical information.

# 14. Medical Knowledge Base

The existing curated RAG knowledge base remains unchanged.

Potential trusted sources:
- WHO.
- CDC.
- NHS.
- Other approved medical references.

ChromaDB remains the vector store.

# 15. Dashboard, History and Reports

The dashboard shall retain:
- Latest assessment.
- Prediction.
- Confidence.
- Severity.
- Recent assessments.
- Health trends where implemented.
- Recovery information.
- Reminders.
- Reports.

History may store:
- User ID.
- Symptoms.
- Predicted disease.
- Confidence.
- Severity.
- Explanation.
- Recommendations.
- Timestamp.

Reports may contain assessment date, symptoms, prediction, confidence, severity, explanation and recommendations, with PDF/CSV support where implemented.

# 16. Reminders

Supported:
- Daily reminders at a selected time.
- Specific-day reminders at a selected time.

Not supported:
- Every X Hours.
- As Needed.

Email reminders support YES/NO actions and synchronize the state with the application.

# 17. Healthcare Provider Data

Provider records may contain:
- Name.
- Specialty.
- Hospital/clinic.
- City/location.
- Address.
- Contact information.
- Hours.
- Other verified fields.

The recommendation system must not invent missing provider information.

# 18. API Requirements

Existing REST APIs shall continue to support:
- Symptoms.
- Diseases.
- Prediction.
- History.
- Recovery plans.
- AI chat.
- Medical knowledge.
- Doctors.
- Hospitals.
- Healthcare recommendations.
- Reports.
- Reminders.
- Health checks.

Routes remain thin and delegate business logic to services.

# 19. Security and UX

The system shall:
- Use Clerk authentication.
- Protect user-specific endpoints.
- Validate inputs.
- Protect API keys.
- Keep secrets in environment variables.
- Avoid exposing internal errors.
- Prevent unauthorized health-record access.

Critical UI flows must have loading, empty and error states. The application must remain responsive and accessible.

# 20. Acceptance Criteria

The updated recommendation workflow is complete when:
1. User submits symptoms.
2. Kaggle-trained ML predicts the disease.
3. The LLM cannot change the disease.
4. The system determines the configured specialty.
5. User provides a location.
6. Available provider data is obtained.
7. LangChain builds a dynamic prompt.
8. Gemini returns structured recommendation data.
9. Recommendations are relevant to disease and location.
10. Provider information is not invented.
11. Existing prediction workflow remains functional.
12. Existing assistant, recovery plan, dashboard, history, reports and reminders remain functional.

# 21. Definition of Done

The project is complete when the core ML prediction, Kaggle training, three models, SHAP, medical metadata, disease/location-aware doctor and hospital recommendations, structured LangChain/Gemini output, AI/RAG assistant, recovery plan, dashboard, history, reports, reminders and authentication work without critical frontend/backend integration errors.

# 22. Medical Disclaimer

SymptomScope AI provides preliminary health information and symptom intelligence. Predictions and recommendations are not a substitute for professional medical diagnosis or treatment. Users should consult qualified healthcare professionals. Severe or life-threatening symptoms require appropriate emergency medical care.
