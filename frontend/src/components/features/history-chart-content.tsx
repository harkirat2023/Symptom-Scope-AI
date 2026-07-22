"use client";

import { useMemo } from "react";
import { Activity, Lightbulb } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendIcon } from "@/components/shared/trend-icon";
import { cn } from "@/lib/utils";
import type { PredictionRecord, AnalyticsResponse } from "@/lib/api/predictions";
import { HealthSummaryBanner } from "@/components/features/dashboard/health-summary-banner";
import { SummaryCharts } from "@/components/features/history/summary-charts";
import { HistoryTimeline } from "@/components/features/history/history-timeline";

export default function HistoryChartContent({
  predictions,
  analytics,
  gridColor,
  textColor,
}: {
  predictions: PredictionRecord[];
  analytics: AnalyticsResponse | undefined;
  gridColor: string;
  textColor: string;
}) {
  const { severityCounts, conditionCounts, symptomClusters } = useMemo(() => {
    const sev: Record<string, number> = {};
    const cond: Record<string, number> = {};
    const symp: Record<string, number> = {};
    for (const p of predictions) {
      sev[p.severity] = (sev[p.severity] ?? 0) + 1;
      cond[p.prediction] = (cond[p.prediction] ?? 0) + 1;
      for (const s of p.symptoms) {
        symp[s] = (symp[s] ?? 0) + 1;
      }
    }
    return {
      severityCounts: Object.entries(sev).map(([name, value]) => ({ name, value })),
      conditionCounts: Object.entries(cond).sort(([, a], [, b]) => b - a).slice(0, 6).map(([name, value]) => ({ name, value })),
      symptomClusters: Object.entries(symp).sort(([, a], [, b]) => b - a).slice(0, 8).map(([name, value]) => ({ name, value })),
    };
  }, [predictions]);

  return (
    <>
      {analytics?.health_summary && (
        <HealthSummaryBanner healthSummary={analytics.health_summary} />
      )}

      <SummaryCharts
        conditionCounts={conditionCounts}
        severityCounts={severityCounts}
        symptomClusters={symptomClusters}
        gridColor={gridColor}
        textColor={textColor}
      />

      {analytics?.symptom_trends && analytics.symptom_trends.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="size-4 text-primary" />
              Symptom Pattern Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
              {analytics.symptom_trends.slice(0, 8).map((st) => (
                <div key={st.symptom} className="flex items-center gap-2 p-2 rounded-lg border">
                  <TrendIcon direction={st.direction} />
                  <div className="min-w-0">
                    <p className="text-xs font-medium truncate">{st.symptom}</p>
                    <p className={cn(
                      "text-xs",
                      st.direction === "increasing" && "text-destructive",
                      st.direction === "decreasing" && "text-success",
                      st.direction === "stable" && "text-muted-foreground",
                      st.direction === "insufficient_data" && "text-muted-foreground"
                    )}>
                      {st.direction === "increasing" && `+${st.change_pct}%`}
                      {st.direction === "decreasing" && `${st.change_pct}%`}
                      {st.direction === "stable" && "Stable"}
                      {st.direction === "insufficient_data" && "Limited"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {analytics?.insights && analytics.insights.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Lightbulb className="size-4 text-warning" />
              Health Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1.5">
              {analytics.insights.slice(0, 4).map((insight, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="mt-1.5 size-1.5 rounded-full bg-primary shrink-0" />
                  {insight}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <HistoryTimeline predictions={predictions} />
    </>
  );
}
