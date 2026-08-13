# SymptomScope AI — UI/UX Design System & Design Specification

**Reference:** Trace – Link Analytics & Attribution Dashboard UI by Suhayel Ahmed Nasim on Dribbble  
**Reference URL:** https://dribbble.com/shots/27637419-Trace-Link-Analytics-Attribution-Dashboard-UI  
**Design Direction:** Clean, analytical, premium SaaS dashboard adapted for a health-intelligence product.

> The Trace reference is used as visual inspiration, not as a literal copy. SymptomScope AI must preserve its own health-product identity, information architecture, safety requirements and accessibility.

---

## 1. Design Objective

Redesign SymptomScope AI as a polished, modern health-intelligence dashboard with the visual clarity of a premium analytics SaaS product.

The interface should communicate:

- Trust
- Clarity
- Intelligence
- Medical seriousness
- Calmness
- Data-driven decision support
- Ease of use

The design should feel significantly more refined than a generic medical dashboard while remaining simple enough for a non-technical user.

---

## 2. Reference Design Analysis

The Trace reference emphasizes a modern analytics-product aesthetic. Its visual language uses a light neutral canvas, dark typography, restrained purple/blue accents, rounded containers, compact navigation and dense-but-organized analytical information.

The reference specifically describes an intelligence panel that surfaces actionable insights, a traffic-flow visualization and a conversion funnel. For SymptomScope, these ideas should be translated into:

- AI Health Insights
- Symptom → Prediction → Recommendation flow
- Health trends
- Prediction confidence
- Severity indicators
- Recovery progress
- AI assistant interactions

The reference palette includes:

- `#F3F3F7` — soft background
- `#384873` — deep blue
- `#B5B5E1` — muted lavender
- `#A1A3AA` — secondary gray
- `#4445BD` — primary indigo
- `#0C0C0F` — primary dark
- `#4B4E50` — secondary dark gray
- `#8B6D51` — warm supporting accent

These colors should be treated as inspiration and adapted for healthcare accessibility rather than copied blindly.

---

## 3. Core Design Philosophy

### 3.1 Analytics Product + Healthcare Product

Use the visual structure of a modern analytics dashboard but replace marketing/attribution concepts with health intelligence.

The UI should make the user feel:

> "This system understands my health information and presents it clearly."

Not:

> "This is a complicated medical administration system."

### 3.2 Information Hierarchy

Every page should follow:

```text
Page title
↓
Short context / status
↓
Primary action
↓
Most important information
↓
Supporting analytics
↓
Detailed information
```

### 3.3 Progressive Disclosure

Do not show every technical detail immediately.

For example:

**Primary result**

Possible condition: Flu

**Supporting information**

Confidence: 89%

**Expandable explanation**

Why this prediction?

- Fever
- Cough
- Fatigue

This prevents the interface from becoming intimidating.

---

# 4. Global Layout

## Desktop

Use a persistent left sidebar with a spacious content area.

```text
┌──────────────────────────────────────────────────────────────┐
│                         Top Header                            │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│   Sidebar     │                 Main Content                 │
│               │                                              │
│ Dashboard     │                                              │
│ Symptom Check │                                              │
│ Recovery Plan │                                              │
│ History       │                                              │
│ Reports       │                                              │
│ Reminders     │                                              │
│               │                                              │
│               │                                              │
│ Settings      │                                              │
└───────────────┴──────────────────────────────────────────────┘
```

## Sidebar

The sidebar should be:

- Fixed/sticky on desktop.
- Compact.
- Icon + label.
- Visually quiet.
- Clearly highlight the active route.
- Collapsible if already supported by the application.
- Full-height.
- Free from unnecessary decorative elements.

Recommended navigation:

1. Dashboard
2. Symptom Checker
3. Recovery Plan
4. History
5. Reports
6. Reminders
7. Settings

Optional:

8. Find Care

---

# 5. Header

The header should contain:

- Page context/breadcrumb.
- Search where useful.
- Notifications/reminders indicator.
- User profile/avatar.
- Minimal actions.

Avoid overcrowding the header.

The header should visually integrate with the sidebar and main canvas instead of appearing as an independent card.

---

# 6. Visual System

## Background

Primary page background:

`#F3F3F7`

Use subtle tonal variations for sections rather than many unrelated card colors.

## Surface

Cards should use:

- White or near-white surface.
- Very subtle border.
- Minimal shadow.
- Medium corner radius.

Avoid heavy glassmorphism.

## Typography

Use a clean modern sans-serif.

Recommended hierarchy:

- H1: 28–32px, semibold/bold.
- H2: 20–24px, semibold.
- H3: 16–18px, semibold.
- Body: 14–16px.
- Supporting text: 12–14px.

Use dark text such as `#0C0C0F`.

Do not use excessively large headings.

---

# 7. Color System

## Primary

Use indigo/blue as the main interaction color.

Reference inspiration:

`#4445BD`

Use it for:

- Primary buttons.
- Active navigation.
- Links.
- Selected states.
- Important chart series.

## Secondary

Muted lavender:

`#B5B5E1`

Use for:

- Secondary chart series.
- Subtle highlights.
- Background accents.

## Success

Use a calm green.

Use only for:

- Completed states.
- Healthy/positive trends.
- Successful operations.

## Warning

Use amber/orange.

Use for:

- Moderate severity.
- Attention-required states.
- Warning banners.

## Critical

Use restrained red.

Use for:

- Severe severity.
- Emergency alerts.
- Destructive actions.

Red should never dominate the entire interface.

---

# 8. Dashboard Design

The dashboard should borrow the reference's analytical density while remaining health-focused.

## Top Section

```text
Good morning, Harkirat
Here's your health overview

[Start Symptom Check]
```

Below it:

```text
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Assessments  │ │ Last Result  │ │ Severity     │ │ Recovery     │
│      12      │ │ Flu          │ │ Moderate     │ │ 68%          │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

Cards should be compact rather than oversized.

---

# 9. Health Intelligence Panel

Create a prominent right-side or upper dashboard panel inspired by Trace's Intelligence panel.

Title:

**Health Intelligence**

Examples:

- Your recent symptom pattern is improving.
- Your latest assessment had moderate severity.
- Consider reviewing your recovery plan.
- Your last assessment was 7 days ago.
- A follow-up reminder is scheduled.

Each insight should have:

- Icon.
- Short explanation.
- Optional confidence/context.
- Optional action.

Example:

```text
Health Intelligence

● Recovery trend improving
  Your recent assessment is less severe than the previous one.

  [View History]

● Follow-up reminder
  Scheduled for tomorrow at 9:00 AM.

  [View Reminder]
```

Do not allow AI-generated insights to present unsupported medical conclusions.

---

# 10. Symptom Checker

The symptom checker should feel like a guided workflow rather than a large form.

## Layout

```text
Step 2 of 4

What symptoms are you experiencing?

[ Search symptoms... ]

Selected
[ Fever × ] [ Cough × ] [ Fatigue × ]

Common symptoms
○ Headache
○ Nausea
○ Sore throat
○ Body ache

                         [Back] [Continue]
```

Include:

- Step indicator.
- Search.
- Selected-symptom chips.
- Common symptom suggestions.
- Clear validation.
- Continue/back controls.

The primary CTA should be visually dominant.

---

# 11. Prediction Results

This is one of the most important pages.

Use a strong result hierarchy.

```text
Assessment Result

Possible condition
FLU

89%
Confidence

Moderate
Severity
```

Then:

```text
Why this prediction?

Fever       ██████████
Cough       ████████
Fatigue     ██████
```

Then:

```text
Recommended next steps
[View Recovery Plan]
[Ask Health Assistant]
[Download Report]
```

Avoid presenting the prediction as a diagnosis.

Use language such as:

- Possible condition.
- Preliminary prediction.
- Model confidence.
- For informational purposes.

---

# 12. Prediction Explanation

The SHAP explanation should be visually understandable.

Avoid exposing raw mathematical SHAP values as the primary UI.

Instead:

```text
Why did the model predict this?

High contribution
● Fever
● Persistent cough

Moderate contribution
● Fatigue

Lower contribution
● Headache
```

Provide an expandable technical explanation if needed.

---

# 13. Severity UI

Use a consistent severity system.

### Mild

Neutral/green visual treatment.

### Moderate

Amber treatment.

### Severe

Red treatment.

Example:

```text
Severity
[ MODERATE ]

Requires attention
Review the recommended next steps and consider professional guidance.
```

Emergency states should use a clearly separated alert component.

---

# 14. Recovery Plan UI

The Recovery Plan should look like an actionable health plan rather than an AI-generated wall of text.

Top:

```text
Recovery Plan
Based on your latest assessment

Condition: Flu
Severity: Moderate

[Generate Recovery Plan]
```

Then sections:

```text
┌────────────────────────────────────┐
│ Today's priorities                 │
│                                    │
│ ✓ Stay hydrated                    │
│ ✓ Rest adequately                  │
│ ✓ Follow recommended care          │
└────────────────────────────────────┘

Nutrition
────────────────────────
Eat
[Food cards]

Limit / Avoid
[Food cards]

Activity
────────────────────────
Recommended
[Activity cards]

Avoid
[Activity cards]

Warning Signs
────────────────────────
[Alert]
```

Keep content scannable.

---

# 15. AI Health Assistant

The assistant should be integrated into the application without blocking the primary page.

Use a floating/right-side panel.

## Current Problem to Avoid

Do not allow the assistant to become an oversized panel that hides the Recovery Plan or dashboard.

## Recommended Design

```text
                           ┌─────────────────────┐
                           │ Health Assistant  × │
                           ├─────────────────────┤
                           │                     │
                           │ AI response         │
                           │                     │
                           │ User question       │
                           │                     │
                           │ AI response         │
                           │                     │
                           ├─────────────────────┤
                           │ Ask about your...   │
                           │                  ↑  │
                           └─────────────────────┘
```

Width:

- Desktop: approximately 360–420px.
- Mobile: full-width bottom sheet/page.

The panel should have:

- Header.
- Clear AI identity.
- Scrollable messages.
- User/assistant distinction.
- Typing/loading state.
- Error state.
- Input.
- Suggested questions.

Suggested prompts:

- "Explain my result."
- "What should I eat?"
- "What should I avoid?"
- "Explain the severity."
- "When should I seek medical care?"

---

# 16. Chat Message Design

User messages should be visually distinct but not overly colorful.

Assistant messages should be clean and readable.

Use Markdown rendering for:

- Lists.
- Bold emphasis.
- Headings.
- Short sections.

Avoid huge text blocks.

Medical disclaimers should appear subtly but clearly.

---

# 17. History Page

Use an analytical table/list inspired by SaaS dashboards.

```text
Assessment History

Date        Condition     Severity     Confidence    Action
------------------------------------------------------------
Aug 12      Flu           Moderate     89%           View
Aug 04      Cold          Mild         82%           View
Jul 27      Fever         Moderate     76%           View
```

Provide filters:

- Date.
- Severity.
- Condition.

Use pagination or virtualization if history grows significantly.

---

# 18. Reports Page

Use compact report cards.

```text
Health Reports

┌──────────────────────────────┐
│ Assessment — Aug 12          │
│ Flu · Moderate · 89%         │
│                              │
│ [View] [PDF] [CSV]           │
└──────────────────────────────┘
```

Do not make downloads visually dominant over health information.

---

# 19. Reminders

Use a clean settings-like list.

```text
Health Reminders

Medication / Follow-up
[ ON ]

Frequency
● Daily
○ Specific days

Time
[ 09:00 AM ]

Days
[ Thu ] [ Sat ]

[Save Reminder]
```

Do not show:

- Every X Hours.
- As Needed.

Email confirmation should support YES/NO actions and synchronize the result back into the application.

---

# 20. Find Care

The healthcare discovery screen should use a split layout:

```text
┌──────────────────────────┬──────────────────────────┐
│ Filters                  │ Map / Location           │
│                          │                          │
│ Specialty                │      ● Hospital          │
│ Distance                 │                          │
│                          │             ● Clinic     │
├──────────────────────────┴──────────────────────────┤
│ Hospital / Doctor Cards                              │
└───────────────────────────────────────────────────────┘
```

Cards should include:

- Name.
- Specialty.
- Distance where available.
- Rating where verified.
- Hours.
- Contact.
- Directions.

---

# 21. Settings

Settings should be simple and grouped.

Sections:

- Profile.
- Account.
- Notifications.
- Reminders.
- Privacy.
- AI preferences.
- Security.

Clerk's profile management should remain visually integrated into the application.

---

# 22. Charts and Data Visualization

Charts should follow the same visual language.

Recommended:

- Line charts for symptom/severity trends.
- Bar charts for assessment frequency.
- Donut charts only where composition is useful.
- Progress bars for recovery.
- Small sparklines for dashboard KPI cards.

Avoid:

- 3D charts.
- Excessive gradients.
- Too many colors.
- Decorative charts without meaning.

---

# 23. Cards

Cards should be:

- Medium rounded.
- Thin bordered.
- Light shadow or no shadow.
- Consistent padding.
- Strong internal hierarchy.

Avoid placing cards inside cards unless there is a clear hierarchy.

Use fewer, larger meaningful sections rather than dozens of tiny boxes.

---

# 24. Buttons

Primary button:

- Indigo background.
- White text.
- Medium radius.
- Clear hover state.

Secondary:

- White/neutral surface.
- Border.
- Dark text.

Danger:

- Reserved for destructive actions.

Button text should describe the action:

- Start Assessment.
- Generate Recovery Plan.
- View Explanation.
- Ask Assistant.
- Download Report.

Avoid generic text such as "Click Here".

---

# 25. Forms

Use:

- Clear labels.
- Short descriptions.
- Consistent input height.
- Visible focus state.
- Inline validation.
- Error messages below the field.

Do not rely only on color to communicate errors.

---

# 26. Empty States

Every data-driven page must have a useful empty state.

Example:

```text
No assessments yet

Complete your first symptom assessment to start
building your health history.

[Start Symptom Check]
```

Avoid blank white areas.

---

# 27. Loading States

Use skeletons instead of blank screens.

For example:

```text
[████████████████]
[██████████]
[████████████████████████]
```

AI interactions should show:

- Thinking.
- Generating.
- Retrieving knowledge.

Do not freeze the UI.

---

# 28. Error States

Errors should be human-readable.

Bad:

`Failed to fetch`

Better:

```text
We couldn't generate your recovery plan.

Your assessment is still saved.

[Retry]
```

Technical error details may be available behind an expandable developer/debug section.

---

# 29. Responsive Design

## Desktop

- Persistent sidebar.
- Multi-column dashboard.
- Right-side AI assistant.
- Dense analytical layout.

## Tablet

- Collapsible sidebar.
- Reduced card columns.
- AI assistant as overlay.

## Mobile

- Sidebar becomes drawer.
- One-column layout.
- Cards stack.
- Charts become horizontally scrollable where necessary.
- AI assistant becomes a bottom sheet/full-screen route.
- Primary actions remain reachable.

Never allow horizontal page overflow.

---

# 30. Micro-Interactions

Use subtle motion for:

- Sidebar selection.
- Card hover.
- Button press.
- Modal opening.
- Chart transitions.
- AI message appearance.
- Loading states.

Animation should be fast and restrained.

Avoid excessive bouncing or decorative animations.

Respect `prefers-reduced-motion`.

---

# 31. Accessibility

The design must support:

- Keyboard navigation.
- Visible focus indicators.
- Screen readers.
- Semantic HTML.
- ARIA labels where required.
- Accessible dialogs.
- Accessible charts with text summaries.
- Sufficient contrast.
- Reduced motion.

Medical warnings must not rely only on red color.

---

# 32. Design Tokens

Recommended base tokens:

```css
--background: #F3F3F7;
--surface: #FFFFFF;
--foreground: #0C0C0F;
--muted: #A1A3AA;
--primary: #4445BD;
--primary-soft: #B5B5E1;
--deep-blue: #384873;
--border: #E5E5EA;
--success: #2F8F62;
--warning: #C58A28;
--danger: #C44747;
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
```

These are starting tokens. Existing project conventions should be preserved where they are technically better.

---

# 33. Component System

Build/reuse components rather than styling every page independently.

Recommended components:

```text
AppShell
Sidebar
Header
PageHeader
StatCard
InsightCard
StatusBadge
SeverityBadge
PredictionCard
ConfidenceCard
ExplanationChart
RecommendationCard
RecoverySection
AIChatPanel
ChatMessage
SearchInput
FilterBar
DataTable
HistoryRow
ReportCard
ReminderCard
EmptyState
ErrorState
LoadingSkeleton
ConfirmDialog
MedicalDisclaimer
EmergencyAlert
```

---

# 34. Page-Level Design Requirements

### Dashboard

Primary purpose: understand current health status quickly.

### Symptom Checker

Primary purpose: complete assessment with minimum friction.

### Results

Primary purpose: understand prediction and next actions.

### Recovery Plan

Primary purpose: follow structured recovery guidance.

### History

Primary purpose: understand previous assessments.

### Reports

Primary purpose: review/export health assessment records.

### Reminders

Primary purpose: configure and manage follow-ups.

### Find Care

Primary purpose: locate appropriate healthcare resources.

### Settings

Primary purpose: manage profile, account and preferences.

---

# 35. AI Safety UX

The UI must visually distinguish:

**ML prediction**

> Generated by the SymptomScope prediction engine.

**Medical knowledge**

> Retrieved from curated medical sources.

**AI-generated response**

> Generated by Groq using available context.

This transparency is essential.

---

# 36. Medical Disclaimer Design

Do not display an enormous disclaimer on every screen.

Use:

- Compact disclaimer near prediction/recovery results.
- Expanded disclaimer in relevant details.
- Persistent access through footer/help.

Emergency warnings must be more prominent than the general disclaimer.

---

# 37. Visual Density

Target a professional analytics-dashboard density.

Avoid:

- Excessive whitespace.
- Huge cards.
- Huge typography.
- Long paragraphs.
- Too many borders.

Aim for:

```text
Clear hierarchy
+
Compact information
+
Strong whitespace between sections
+
Minimal decoration
```

The reference design demonstrates that high information density can still feel clean when hierarchy is strong.

---

# 38. What NOT to Copy From the Reference

Do not directly copy:

- Trace branding.
- Trace logo.
- Marketing/attribution terminology.
- Link analytics concepts.
- Exact screen layouts.
- Exact illustrations.
- Exact proprietary visual assets.

Only the broader design principles should inspire SymptomScope:

- SaaS analytics structure.
- Clean light canvas.
- Strong hierarchy.
- Compact navigation.
- Data-focused cards.
- Actionable intelligence panels.
- Restrained color usage.
- Professional visual language.

---

# 39. Implementation Constraints

The redesign must work with the existing project stack.

Do not introduce a new frontend framework.

Preferred/current technologies:

- Next.js.
- React.
- TypeScript.
- Tailwind CSS.
- shadcn/ui.
- React Hook Form.
- Zod.
- Existing API/data-fetching architecture.

Do not replace working backend functionality merely for visual changes.

Do not break:

- Clerk authentication.
- Symptom prediction.
- SHAP explanations.
- Recovery Plan.
- AI assistant.
- LangChain/RAG.
- Groq integration.
- ChromaDB.
- MongoDB.
- History.
- Reports.
- Reminders.
- Doctor/hospital functionality.

---

# 40. Implementation Priority

### P0 — Global Shell

- Sidebar.
- Header.
- Background.
- Typography.
- Design tokens.
- Responsive structure.

### P1 — Core Health Flow

- Dashboard.
- Symptom Checker.
- Results.
- Recovery Plan.

### P2 — Intelligence

- AI Assistant.
- Health Intelligence panel.
- SHAP explanation.
- Health analytics.

### P3 — Supporting Features

- History.
- Reports.
- Reminders.
- Find Care.
- Settings.

### P4 — Polish

- Loading states.
- Empty states.
- Error states.
- Accessibility.
- Responsive behavior.
- Micro-interactions.

---

# 41. Design Acceptance Criteria

The redesign is complete when:

- All major pages share one coherent visual system.
- Sidebar/header are consistent.
- Dashboard feels like a premium analytics product.
- Primary health information is immediately scannable.
- Prediction results are clearly distinguished from diagnosis.
- Severity states are visually consistent.
- AI assistant does not obstruct the main workflow.
- Recovery Plan is readable and actionable.
- Charts have meaningful purposes.
- Empty/loading/error states exist.
- Mobile layout works without horizontal overflow.
- Keyboard navigation works.
- Contrast is accessible.
- Existing functionality remains intact.
- No backend/API workflow is broken.
- No new unnecessary technology is introduced.

---

# 42. Final Design Direction

The final SymptomScope AI interface should feel like:

**"A premium health-intelligence SaaS platform."**

It should combine:

```text
Trace-inspired analytics clarity
            +
Medical product trust
            +
AI intelligence
            +
Explainable ML
            +
Simple user workflows
```

The goal is not to make SymptomScope look like a generic hospital website. The goal is to create a modern, intelligent and trustworthy health platform where complex ML/AI output becomes understandable and actionable for ordinary users.
