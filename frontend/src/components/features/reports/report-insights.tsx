"use client";

import { Lightbulb } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface ReportInsightsProps {
  analytics: AnalyticsResponse | undefined;
}

export function ReportInsights({ analytics }: ReportInsightsProps) {
  if (!analytics?.insights || analytics.insights.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Lightbulb className="size-4 text-warning" />
          Actionable Insights
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {analytics.insights.map((insight, i) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              <span
                className={cn(
                  "mt-1.5 size-2 rounded-full shrink-0",
                  insight.includes("severe") || insight.includes("below 60%")
                    ? "bg-destructive"
                    : insight.includes("Rising") || insight.includes("recurring")
                    ? "bg-warning" : "bg-primary"
                )}
              />
              {insight}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
