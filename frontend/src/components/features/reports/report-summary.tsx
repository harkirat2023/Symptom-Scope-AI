"use client";

import { HeartPulse } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ReportResponse } from "@/lib/api/predictions";

interface ReportSummaryProps {
  report: ReportResponse;
}

export function ReportSummary({ report }: ReportSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <HeartPulse className="size-5 text-primary" />
          Health Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-3 rounded-lg bg-muted/50">
            <dt className="text-xs text-muted-foreground">Total Predictions</dt>
            <dd className="text-2xl font-semibold">{report.total_predictions ?? 0}</dd>
          </div>
          <div className="p-3 rounded-lg bg-muted/50">
            <dt className="text-xs text-muted-foreground">Most Common Condition</dt>
            <dd className="text-lg font-semibold truncate" title={report.most_common_disease ?? "N/A"}>
              {report.most_common_disease ?? "N/A"}
            </dd>
          </div>
          <div className="p-3 rounded-lg bg-muted/50">
            <dt className="text-xs text-muted-foreground">Average Confidence</dt>
            <dd className="text-2xl font-semibold text-primary">
              {report.avg_confidence ? `${report.avg_confidence.toFixed(1)}%` : "N/A"}
            </dd>
          </div>
          <div className="p-3 rounded-lg bg-muted/50">
            <dt className="text-xs text-muted-foreground">Severe Cases</dt>
            <dd className="text-2xl font-semibold text-destructive">{report.severe_count ?? 0}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
