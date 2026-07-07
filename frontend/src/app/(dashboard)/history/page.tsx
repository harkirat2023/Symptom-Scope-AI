"use client";

import nextDynamic from "next/dynamic";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import {
  History as HistoryIcon,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { fetchUserReports, fetchAnalytics } from "@/lib/api/predictions";

export const dynamic = "force-dynamic";

const HistoryChartContent = nextDynamic(
  () => import("@/components/features/history-chart-content"),
  { ssr: false }
);

export default function HistoryPage() {
  const { userId, getToken } = useAuth();
  const { resolvedTheme } = useTheme();

  const isDark = resolvedTheme === "dark";

  const { data: report, isLoading, error: reportError } = useQuery({
    queryKey: ["report", userId],
    queryFn: async () => {
      const token = await getToken();
      return fetchUserReports(userId!, token ?? undefined);
    },
    enabled: !!userId,
  });

  const { data: analytics, error: analyticsError } = useQuery({
    queryKey: ["analytics", userId, "6m"],
    queryFn: async () => {
      const token = await getToken();
      return fetchAnalytics(userId!, "6m", token ?? undefined);
    },
    enabled: !!userId,
  });

  const predictions = report?.predictions ?? [];

  const gridColor = isDark ? "#334155" : "#e2e8f0";
  const textColor = isDark ? "#94a3b8" : "#64748b";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Health History</h1>
        <p className="text-muted-foreground">
          Your complete symptom check history and health patterns
        </p>
      </div>

      {isLoading && (
        <div className="space-y-4" role="status" aria-label="Loading history">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-5 w-48 mb-2" />
                <Skeleton className="h-4 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {reportError && (
        <Alert variant="destructive" role="alert" aria-live="assertive">
          <AlertTriangle className="size-4" />
          <AlertTitle>Error loading history</AlertTitle>
          <AlertDescription>
            Unable to load your health history. Please try again later.
          </AlertDescription>
        </Alert>
      )}

      {analyticsError && (
        <Alert variant="destructive" role="alert" aria-live="assertive">
          <AlertTriangle className="size-4" />
          <AlertTitle>Error loading analytics</AlertTitle>
          <AlertDescription>
            Unable to load analytics data. Some charts may not display.
          </AlertDescription>
        </Alert>
      )}

      {!isLoading && !reportError && predictions.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <HistoryIcon className="size-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No history available</h3>
            <p className="text-muted-foreground">
              Use the Symptom Checker to make your first prediction.
            </p>
          </CardContent>
        </Card>
      )}

      {predictions.length > 0 && (
        <HistoryChartContent
          predictions={predictions}
          analytics={analytics}
          gridColor={gridColor}
          textColor={textColor}
        />
      )}
    </div>
  );
}