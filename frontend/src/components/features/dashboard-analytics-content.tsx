"use client";

import { SummaryCards } from "@/components/features/dashboard/summary-cards";
import { HealthSummaryBanner } from "@/components/features/dashboard/health-summary-banner";
import { DiseaseChartsRow } from "@/components/features/dashboard/disease-charts-row";
import { TrendChartsRow } from "@/components/features/dashboard/trend-charts-row";
import { SymptomsConfidenceRow } from "@/components/features/dashboard/symptoms-confidence-row";
import { SymptomProgressTrends } from "@/components/features/dashboard/symptom-progress-trends";
import { RecurringConditions } from "@/components/features/dashboard/recurring-conditions";
import { HealthInsights } from "@/components/features/dashboard/health-insights";
import { SymptomTimeline } from "@/components/features/dashboard/symptom-timeline";
import { RecommendationHistory } from "@/components/features/dashboard/recommendation-history";
import { ReminderDashboardCard } from "@/components/features/reminders/reminder-dashboard-card";
import RiskScoreDashboardCard from "@/components/features/risk-score/risk-score-dashboard-card";
import type { AnalyticsResponse, PredictionRecord } from "@/lib/api/predictions";

export default function DashboardAnalyticsContent({
  a,
  gridColor,
  textColor,
  predictions,
}: {
  a: AnalyticsResponse;
  gridColor: string;
  textColor: string;
  predictions?: PredictionRecord[];
}) {
  return (
    <>
      <SummaryCards summary={a.summary} />

      {a.health_summary && (
        <HealthSummaryBanner healthSummary={a.health_summary} />
      )}

      <ReminderDashboardCard />

      <RiskScoreDashboardCard />

      <DiseaseChartsRow a={a} gridColor={gridColor} textColor={textColor} />

      <TrendChartsRow a={a} gridColor={gridColor} textColor={textColor} />

      <SymptomsConfidenceRow a={a} gridColor={gridColor} textColor={textColor} />

      {predictions && <SymptomTimeline predictions={predictions} />}

      <SymptomProgressTrends symptomTrends={a.symptom_trends} />

      {predictions && <RecommendationHistory predictions={predictions} />}

      <RecurringConditions recurringConditions={a.recurring_conditions} />

      <HealthInsights insights={a.insights} />
    </>
  );
}
