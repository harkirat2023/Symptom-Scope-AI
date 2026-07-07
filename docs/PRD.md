## **13. System Workflow & End-to-End User Journey** 

## **Overview** 

SymptomScope AI follows a healthcare intelligence workflow that transforms raw symptom inputs into actionable health insights through Machine Learning, explainable AI, severity assessment, precaution recommendations, doctor discovery, emergency detection, and health analytics. 

## **High-Level System Flow** 

```
User
 ↓
Authentication
 ↓
Symptom Input
 ↓
Data Validation
 ↓
Feature Engineering
 ↓
Disease Prediction Models
(Decision Tree + Random Forest)
 ↓
Confidence Score Calculation
 ↓
Explainable AI Layer
 ↓
Severity Classification
 ↓
Precaution Recommendation Engine
 ↓
Doctor Recommendation Engine
 ↓
Emergency Detection Engine
 ↓
MongoDB Storage
 ↓
Dashboard Analytics
 ↓
Report Generation
```

1 

## **Step 1: User Authentication** 

The user creates an account or logs in. 

Supported Methods: 

- Email + Password 

- Google Login 

- OTP Authentication 

Purpose: 

- Secure medical records 

- Personalized health tracking 

- Historical prediction storage 

Output: 

Authenticated User Session 

## **Step 2: Symptom Collection** 

The user enters symptoms through the symptom checker interface. 

Inputs: 

- Symptoms 

- Age 

- Gender (Optional) 

- Existing Conditions (Optional) 

- Symptom Duration 

- Pain Level (Optional) 

Example Input: 

```
{
"symptoms":[
"fever",
"dry cough",
"fatigue",
"headache"
],
"age":22,
"gender":"male"
}
```

Purpose: 

2 

Collect sufficient information for disease prediction. 

## **Step 3: Data Validation** 

Backend validates: 

- Required fields 

- Duplicate symptoms 

- Invalid symptom names 

- Missing values 

Validation Rules: 

- At least one symptom required 

- Supported symptom names only 

- Age must be valid 

Output: 

Validated symptom payload 

## **Step 4: Feature Engineering Pipeline** 

Raw symptom data is transformed into machine-learning-ready features. 

Activities: 

- Symptom encoding 

- Missing value handling 

- Feature normalization 

- Data transformation 

Example: 

Input: 

```
Fever
Dry Cough
Fatigue
Headache
```

Encoded Vector: 

3 

```
[
1,1,1,1,0,0,0,0...
]
```

Purpose: 

Convert human-readable symptoms into numerical model inputs. 

## **Step 5: Disease Prediction Engine** 

Two machine learning models run simultaneously. 

Models: 

## **Decision Tree** 

Responsibilities: 

- Fast prediction 

- Easy explainability 

## **Random Forest** 

Responsibilities: 

- Higher accuracy 

- Probability estimation • Confidence calculation 

Inputs: 

Encoded symptom vector 

Output: 

Predicted disease probabilities 

Example: 

```
{
"Influenza":0.92,
"Common Cold":0.05,
"Bronchitis":0.03
}
```

4 

## **Step 6: Confidence Score Calculation** 

Confidence score is calculated using prediction probabilities. 

Formula: 

```
Confidence Score =
Highest Probability × 100
```

Example: 

```
Influenza Probability = 0.92
Confidence Score = 92%
```

Purpose: 

Communicate prediction certainty. 

## **Step 7: Alternative Disease Suggestions** 

Instead of returning a single prediction, the system provides top probable diseases. 

Example: 

```
{
"primaryPrediction":"Influenza",
"confidence":92,
"alternatives":[
"Common Cold",
"Bronchitis"
]
}
```

Purpose: 

Reduce overconfidence and improve transparency. 

## **Step 8: Explainable AI Layer** 

The system identifies symptoms that most influenced the prediction. 

5 

Information Shown: 

- Most influential symptoms 

- Feature importance ranking 

Example: 

Prediction: 

```
Influenza
```

Top Contributing Symptoms: 

`1. Fever` 

`2. Dry Cough` 

`3. Fatigue` 

`4. Headache` 

Purpose: 

Improve trust and transparency. 

## **Step 9: Severity Classification Engine** 

Each disease belongs to a predefined severity category. 

Categories: 

## **Mild** 

Examples: 

- Common Cold 

- Allergies 

## **Moderate** 

Examples: 

- Influenza 

- Bronchitis 

6 

## **Severe** 

Examples: 

- Heart Attack • Stroke • Pneumonia 

Output Example: 

```
{
"severity":"Moderate"
}
```

Purpose: 

Help users understand urgency. 

## **Step 10: Precaution Recommendation Engine** 

The system maps diseases to healthcare precautions. 

Example: 

Disease: 

```
Influenza
```

Precautions: 

```
[
"Drink plenty of fluids",
"Rest adequately",
"Monitor temperature",
"Visit physician if symptoms worsen"
]
```

Purpose: 

Provide actionable health guidance. 

7 

## **Step 11: Doctor Recommendation Engine** 

Based on: 

- User Location 

- Disease Category 

- Medical Specialty Required 

The system recommends healthcare providers. 

Example: 

Predicted Disease: 

```
Pneumonia
```

Recommended Specialists: 

```
Pulmonologist
General Physician
```

Displayed Information: 

- Name 

- Rating 

- Distance • Availability 

Purpose: 

Connect users with professional medical care. 

## **Step 12: Emergency Detection Engine** 

Emergency alerts are triggered under predefined conditions. 

Trigger Rules: 

```
Severity = Severe
OR
Confidence > 90%
for critical diseases
```

8 

Critical Diseases: 

- Stroke 

- Heart Attack 

- Severe Respiratory Distress 

Actions: 

- Emergency Popup 

- Nearby Hospitals 

- Ambulance Contact 

- Telemedicine Consultation 

Purpose: 

Support immediate intervention during emergencies. 

## **Step 13: Prediction Storage** 

Every prediction is stored in MongoDB. 

Prediction Record: 

```
{
"userId":"123",
"symptoms":[
"fever",
"cough"
],
"prediction":"Influenza",
"confidence":92,
"severity":"Moderate",
"timestamp":"2026-06-10"
}
```

Purpose: 

Enable health history tracking. 

## **Step 14: Dashboard Analytics** 

The dashboard aggregates prediction history. 

Sections: 

9 

## **Overview** 

- Latest Prediction 

- Confidence Score 

- Severity 

## **Symptom Timeline** 

- Historical symptom records 

## **Prediction Analytics** 

- Disease frequency • Severity trends 

## **Recommendation History** 

- Previous precautions • Previous doctor suggestions 

Purpose: 

Continuous health monitoring. 

## **Step 15: Report Generation** 

Users can export reports. 

Formats: 

- PDF 

- CSV 

Report Includes: 

- Symptom History 

- Predictions 

- Confidence Scores 

- Severity Trends 

- Precautions 

- Doctor Recommendations 

Purpose: 

Share medical history with healthcare providers. 

10 

## **Example User Journey** 

## **Scenario: Student with Flu Symptoms** 

User: 

Rahul 22 Years Old 

Symptoms: 

- Fever 

- Dry Cough 

- Headache 

- Fatigue 

## **Input** 

```
{
"symptoms":[
"fever",
"dry cough",
"headache",
"fatigue"
],
"age":22
}
```

## **Prediction Output** 

```
{
"predictedDisease":"Influenza",
"confidence":92,
"severity":"Moderate",
"alternatives":[
"Common Cold",
"Bronchitis"
]
}
```

## **Explainability** 

```
Top Contributing Symptoms
```

```
1. Fever
2. Dry Cough
```

11 

`3. Fatigue` 

`4. Headache` 

## **Precautions** 

```
Drink fluids
Rest adequately
Monitor temperature
Visit physician if symptoms worsen
```

## **Recommended Doctors** 

```
Dr. Sharma
General Physician
Dr. Singh
Pulmonologist
```

## **Stored in Dashboard** 

```
Prediction:
Influenza
Confidence:
92%
Severity:
Moderate
Date:
10 June 2026
```

## **Emergency Example** 

Symptoms: 

- Chest Pain 

- Left Arm Pain 

- Sweating 

- Shortness of Breath 

Prediction: 

12 

```
Heart Attack
```

Confidence: 

```
95%
```

Severity: 

```
Severe
```

Emergency Alert: 

- ⚠ `Immediate Medical Attention Required` 

Actions Available: 

- Call Ambulance 

- View Nearby Hospitals 

- Start Teleconsultation 

This workflow demonstrates the complete lifecycle of symptom analysis from symptom entry to healthcare action within SymptomScope AI. 

13 

