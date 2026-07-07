# Feature Components

Feature-specific UI components for SymptomScope AI.

## Structure

| Directory / File | Purpose |
|-----------------|---------|
| `header.tsx` | Landing page header with auth-aware navigation |
| `hero-section.tsx` | Landing page hero with CTA |
| `features-section.tsx` | Feature highlights for landing page |
| `how-it-works-section.tsx` | Step-by-step explanation |
| `footer.tsx` | Landing page footer |
| `theme-init.tsx` | Dark mode initialization script |
| `step-indicator.tsx` | Multi-step wizard progress indicator |
| `symptom-selection-step.tsx` | Step 1 of symptom checker (symptom search) |
| `details-step.tsx` | Step 2 of symptom checker (age, gender, duration) |
| `analyzing-step.tsx` | Step 3 loading animation |
| `prediction-results.tsx` | Step 4 results display |
| `dashboard-analytics-content.tsx` | Dashboard analytics orchestrator |
| `history-chart-content.tsx` | History page charts orchestrator |
| `reports-chart-content.tsx` | Reports page with export section |
| `dashboard/` | Dashboard sub-components (summary, charts, insights) |
| `history/` | History sub-components (timeline, charts) |

## Conventions

- Each component is ≤300 lines
- Business logic lives in services, not components
- All async data uses TanStack Query (server state)
- Local UI state uses Zustand (client state)
