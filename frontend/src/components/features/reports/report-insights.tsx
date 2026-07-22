"use client";

import { HealthInsights } from "@/components/features/dashboard/health-insights";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface ReportInsightsProps {
  analytics: AnalyticsResponse | undefined;
}

export function ReportInsights({ analytics }: ReportInsightsProps) {
  if (!analytics?.insights || analytics.insights.length === 0) return null;
  return <HealthInsights insights={analytics.insights} />;
}
