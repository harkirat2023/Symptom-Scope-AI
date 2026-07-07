# Emergency Action Buttons — Implementation Report

**Date:** 2026-06-11  
**Scope:** Emergency alert banner, EmergencyActionPanel, trigger conditions

---

## 1. Files Modified

| # | File | Change |
|---|---|---|
| 1 | `frontend/src/components/features/prediction-results.tsx` | Pass `predictedDisease` prop to `EmergencyActionPanel` |
| 2 | `frontend/src/components/features/__tests__/emergency-action-panel.test.tsx` | **NEW** — 8 tests covering buttons, dialogs, accessibility |

### No changes to:
- `EmergencyActionPanel` — already fully implemented
- `DoctorRecommendationCard` — already fully implemented
- `PredictionsResponse` / API types — already included `doctor_recommendations`, `emergency.explanation`
- `prediction-results.tsx` layout — already renders the emergency banner, panel, and doctor cards

---

## 2. Components

### Emergency Alert Banner (`prediction-results.tsx:40-64`)

- Full-width banner with `border-destructive` and `bg-destructive/5`
- `AlertTriangle` icon in a circular container
- Title: "Immediate Medical Attention Recommended"
- Description with emergency reason text from `prediction.emergency.reasons`
- Triggered by `prediction.emergency.is_emergency`

### EmergencyActionPanel (`emergency-action-panel.tsx`)

| Element | Implementation |
|---|---|
| **Call Ambulance** | Destructive button, `tel:911` link, `aria-label="Call ambulance immediately"` |
| **Nearby Hospitals** | Opens dialog fetching `fetchHospitals({ emergency_only: true })` via TanStack Query; shows `HospitalCard` with name, location, rating, distance, 24/7 badge, phone |
| **Teleconsultation** | Opens dialog listing Practo, Apollo 24/7, 1mg; includes disease-specific text when `predictedDisease` prop is provided |
| **Loading state** | Hospitals dialog shows `Skeleton` placeholders during fetch |
| **Empty state** | Dialog shows "No emergency hospitals found" message |

### DoctorRecommendationCard (`doctor-recommendation-card.tsx`)

| Element | Present |
|---|---|
| Doctor photo / initials avatar | Yes |
| Name | Yes |
| Specialty | Yes |
| Rating (star icon) | Yes |
| Distance (km) | Yes |
| Availability | Yes |
| Book Consultation button | Yes (links to Practo) |

---

## 3. Trigger Conditions

Actions are shown in `prediction-results.tsx` only when:

```
prediction.emergency.is_emergency === true
```

The backend sets `is_emergency` based on:
- **Severity = Severe** (via `severity_triggered` field)
- **Critical disease detected** (via `confidence_triggered` / `escalation_triggered` fields)

No frontend logic was added or changed for triggering — the existing backend-driven `emergency` object is used as-is.

---

## 4. Accessibility

| Requirement | Status |
|---|---|
| `aria-label` on action buttons | ✅ All three buttons |
| `role="group"` on action panel | ✅ "Emergency action options" |
| Dialog `aria-label` | ✅ Both hospitals and teleconsultation dialogs |
| `tel:` protocol for call | ✅ `window.location.assign("tel:911")` |
| `_blank` links use `noopener` | ✅ Book Consultation button |
| Color contrast (destructive red) | ✅ DESIGN.md compliant |
| Mobile responsive | ✅ `flex-col sm:flex-row` layout |

---

## 5. Tests Added

**File:** `emergency-action-panel.test.tsx` (8 tests)

| Test | Verifies |
|---|---|
| Renders section heading | "Recommended Actions" is visible |
| Renders Call Ambulance button | Button with label "Call ambulance immediately" |
| Renders Nearby Hospitals button | Button with label "Find nearby hospitals" |
| Renders Teleconsultation button | Button with label "Start teleconsultation" |
| Accessible role group | `role="group"` with proper label |
| Hospitals dialog opens | Click triggers dialog with "Nearby Hospitals with Emergency Services" |
| Teleconsultation dialog opens | Click triggers dialog with "Teleconsultation" |
| Predicted disease in teleconsultation | When `predictedDisease="Influenza"` prop is passed, dialog shows "related to Influenza" |

---

## 6. Remaining PRD Gaps

| Gap | Note |
|---|---|
| Real telemedicine API integration | Teleconsultation dialog lists Practo, Apollo 24/7, 1mg as static info — no actual API integration for booking |
| Google Maps integration for hospitals | Hospitals list uses static database; no map view per Phase 2 of TECHSTACK |
| Doctor recommendation cards from live API | `doctor_recommendations` come from the prediction response; no standalone doctor search API integration on results page |
| Intermediate labels on pain slider | Pre-existing DESIGN.md gap (not in scope) |
