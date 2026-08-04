# Recovery Plan Module

## Architecture Overview

The Recovery Plan module provides personalized, evidence-based recovery guidance after a disease prediction. It follows a **hybrid approach**:

1. **Structured Templates** - Each supported disease has a verified recovery template stored as the primary source of truth
2. **AI Personalization** - LangChain + Gemini personalizes the presentation based on user context (disease, severity, confidence, symptoms, demographics)

## Database Design

### Collection: `recovery_plans`

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Primary key |
| `userId` | string | Clerk user ID |
| `predictionId` | string | Reference to prediction record |
| `disease` | string | Predicted disease name |
| `confidence` | float | Prediction confidence (0-100) |
| `severity` | string | mild/moderate/severe |
| `symptoms` | array[string] | User-reported symptoms |
| `planData` | object | Full recovery plan JSON |
| `isRegenerated` | boolean | Whether plan was regenerated |
| `regenerationCount` | int | Number of regenerations |
| `createdAt` | datetime | Creation timestamp |
| `updatedAt` | datetime | Last update timestamp |

### PlanData Structure

```json
{
  "recovery_timeline": ["Week 1: ...", "Week 2: ...", "Week 3-4: ...", "Month 2+: ..."],
  "diet_recommendations": {
    "general_principles": "...",
    "specific_nutrients": "..."
  },
  "foods_to_eat": ["Food 1 - reason", "Food 2 - reason"],
  "foods_to_avoid": ["Food 1 - reason", "Food 2 - reason"],
  "hydration_advice": "...",
  "sleep_recommendation": "...",
  "exercise_recommendation": "...",
  "daily_physical_activity": ["Activity 1", "Activity 2"],
  "lifestyle_changes": ["Change 1", "Change 2"],
  "medicines_disclaimer": "...",
  "when_to_visit_doctor": ["Sign 1", "Sign 2"],
  "emergency_warning_signs": ["Sign 1", "Sign 2"],
  "mental_wellness_tips": ["Tip 1", "Tip 2"],
  "recovery_checklist": ["Item 1", "Item 2"],
  "progress_tracker": {
    "week_1": "Goals",
    "week_2": "Goals",
    "week_3": "Goals",
    "week_4": "Goals"
  }
}
```

## API Endpoints

### GET `/api/v1/predictions/latest`
- Returns the latest prediction for the authenticated user
- Used to automatically load context for recovery plan generation

### POST `/api/v1/recovery-plan/generate`
- Body: `{ "prediction_id": "..." }`
- Generates a new recovery plan using LLM personalization
- Stores in MongoDB
- Returns full `RecoveryPlanResponse`

### GET `/api/v1/recovery-plan/latest`
- Returns the latest recovery plan for the user
- Auto-loads on Recovery Plan page visit

### GET `/api/v1/recovery-plan/history`
- Returns paginated list of all recovery plans for the user

### POST `/api/v1/recovery-plan/regenerate`
- Body: `{ "plan_id": "..." }`
- Regenerates the AI-personalized explanation using same template
- Increments `regenerationCount`

## User Workflow

1. **Login** → User authenticates via Clerk
2. **Predict** → User completes symptom checker, gets disease prediction
3. **View Results** → User sees prediction results
4. **Navigate** → User clicks "Recovery Plan" in sidebar
5. **Auto-load** → Page fetches latest prediction automatically
6. **Generate** → User clicks "Generate Recovery Plan" or it auto-generates
7. **Display** → Recovery plan shown in tabbed interface:
   - Overview (timeline, checklist, progress)
   - Diet & Lifestyle (foods, hydration, sleep, exercise)
   - Warnings (doctor visits, emergency signs, mental wellness)
8. **Regenerate** → User can regenerate AI explanation without changing template
9. **History** → Previous plans accessible via history

## AI Personalization Flow

```
Template (Source of Truth)
       ↓
LLM Prompt with Context:
  - Disease name
  - Severity level
  - Confidence score
  - User symptoms
  - Age, gender, existing conditions
       ↓
Gemini 1.5 Flash (LangChain)
       ↓
Personalized JSON Output
       ↓
Stored in MongoDB + Returned to Frontend
```

**Constraints Enforced:**
- Never changes diagnosis
- Never modifies confidence/severity
- Never prescribes medications
- Never recommends dosages
- Always includes medical disclaimer

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No prediction exists | Prompts user to complete symptom assessment |
| LLM fails | Falls back to structured default plan |
| MongoDB unavailable | Returns 500 with graceful error |
| Invalid prediction ID | Returns 404 |
| Unauthorized access | Returns 403 |

## Frontend Components

### Page: `/recovery-plan`
- Auto-detects latest prediction
- Shows disease summary card
- Tabbed interface:
  - **Overview**: Timeline, Foods, Hydration, Sleep, Exercise, Lifestyle, Checklist, Progress
  - **Diet & Lifestyle**: Diet principles, Foods to Eat/Avoid
  - **Warnings**: Doctor visits, Emergency signs, Mental Wellness, Medication Disclaimer
- Generate/Regenerate buttons
- Loading states and error handling

### Sidebar Integration
- Added "Recovery Plan" with HeartPulse icon
- Active state highlighting

## Responsive Design
- Mobile-first layout
- Tabs collapse on small screens
- Cards stack vertically
- Scrollable content areas

## Dark Mode Support
- Uses existing CSS variables
- All components respect theme

## Future Improvements

1. **Template Management Admin UI** - CRUD for disease templates
2. **PDF Export** - Download recovery plan as PDF
3. **Email/SMS Delivery** - Send plan to patient
4. **Progress Tracking** - User marks checklist items, tracks over time
5. **Multi-language Support** - Template translations
6. **Clinical Integration** - FHIR/HL7 export for providers
7. **RAG Enhancement** - Ground LLM with clinical guidelines
8. **Telemedicine Link** - Direct booking from "When to Visit Doctor"