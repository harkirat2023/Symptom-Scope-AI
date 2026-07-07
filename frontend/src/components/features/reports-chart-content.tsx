"use client";

import { motion } from "framer-motion";
import { ReportSummary } from "@/components/features/reports/report-summary";
import { ReportCharts } from "@/components/features/reports/report-charts";
import { ReportPredictionHistory } from "@/components/features/reports/report-prediction-history";
import { ReportInsights } from "@/components/features/reports/report-insights";
import { ReportExport } from "@/components/features/reports/report-export";
import type { ReportResponse, AnalyticsResponse } from "@/lib/api/predictions";

export default function ReportsChartContent({
  report,
  analytics,
  gridColor,
  textColor,
  userId,
  getToken,
}: {
  report: ReportResponse;
  analytics: AnalyticsResponse | undefined;
  gridColor: string;
  textColor: string;
  userId?: string;
  getToken?: () => Promise<string | null>;
}) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <ReportSummary report={report} />

      <ReportCharts
        report={report}
        analytics={analytics}
        gridColor={gridColor}
        textColor={textColor}
      />

      <ReportPredictionHistory report={report} />

      <ReportInsights analytics={analytics} />

      <ReportExport userId={userId} getToken={getToken} />
    </motion.div>
  );
}
