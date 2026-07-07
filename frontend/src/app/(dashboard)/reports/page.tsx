"use client";

import nextDynamic from "next/dynamic";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import {
  FileText,
  AlertCircle,
} from "lucide-react";

export const dynamic = "force-dynamic";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { fetchUserReports, fetchAnalytics } from "@/lib/api/predictions";
import { useDashboardStore } from "@/lib/stores/dashboard-store";

const ReportsChartContent = nextDynamic(
  () => import("@/components/features/reports-chart-content"),
  { ssr: false }
);

export default function ReportsPage() {
  const { userId, getToken } = useAuth();
  const { resolvedTheme } = useTheme();
  const selectedRange = useDashboardStore((s) => s.selectedTimeRange);

  const isDark = resolvedTheme === "dark";

  const { data: report, isLoading, error } = useQuery({
    queryKey: ["report", userId],
    queryFn: async () => {
      const token = await getToken();
      return fetchUserReports(userId!, token ?? undefined);
    },
    enabled: !!userId,
  });

  const { data: analytics } = useQuery({
    queryKey: ["analytics", userId, selectedRange],
    queryFn: async () => {
      const token = await getToken();
      return fetchAnalytics(userId!, selectedRange, token ?? undefined);
    },
    enabled: !!userId,
  });

  const gridColor = isDark ? "#334155" : "#e2e8f0";
  const textColor = isDark ? "#94a3b8" : "#64748b";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-muted-foreground">
            Detailed health reports and actionable insights
          </p>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-4" role="status" aria-label="Loading reports">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      )}

      {error && (
        <Alert variant="destructive" role="alert" aria-live="assertive">
          <AlertCircle className="size-4" />
          <AlertTitle>Error loading reports</AlertTitle>
          <AlertDescription>
            Unable to load your report data. Please try again later.
          </AlertDescription>
        </Alert>
      )}

      {report && (
        <ReportsChartContent
          report={report}
          analytics={analytics}
          gridColor={gridColor}
          textColor={textColor}
          userId={userId ?? undefined}
          getToken={getToken}
        />
      )}

      {!isLoading && !report && !error && (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="size-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No reports available</h3>
            <p className="text-muted-foreground">
              Use the Symptom Checker to generate your first prediction report.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}