"use client";

import nextDynamic from "next/dynamic";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useTheme } from "next-themes";
import {
  Stethoscope,
  Activity,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import {
  fetchAnalytics,
  fetchUserReports,
} from "@/lib/api/predictions";
import { useDashboardStore } from "@/lib/stores/dashboard-store";

export const dynamic = "force-dynamic";

const RANGE_OPTIONS = [
  { value: "1m" as const, label: "1 Month" },
  { value: "3m" as const, label: "3 Months" },
  { value: "6m" as const, label: "6 Months" },
  { value: "1y" as const, label: "1 Year" },
];

const DashboardAnalyticsContent = nextDynamic(
  () => import("@/components/features/dashboard-analytics-content"),
  { ssr: false }
);

export default function DashboardPage() {
  const { userId, getToken } = useAuth();
  const { resolvedTheme } = useTheme();
  const selectedRange = useDashboardStore((s) => s.selectedTimeRange);
  const setRange = useDashboardStore((s) => s.setSelectedTimeRange);

  const isDark = resolvedTheme === "dark";

  const { data: report } = useQuery({
    queryKey: ["report", userId],
    queryFn: async () => {
      const token = await getToken();
      return fetchUserReports(userId!, token ?? undefined);
    },
    enabled: !!userId,
  });

  const {
    data: analytics,
    isLoading: analyticsLoading,
    error: analyticsError,
  } = useQuery({
    queryKey: ["analytics", userId, selectedRange],
    queryFn: async () => {
      const token = await getToken();
      return fetchAnalytics(userId!, selectedRange, token ?? undefined);
    },
    enabled: !!userId,
  });

  const a = analytics;

  const gridColor = isDark ? "#334155" : "#e2e8f0";
  const textColor = isDark ? "#94a3b8" : "#64748b";

  if (analyticsError) {
    return (
      <div className="space-y-6" role="alert" aria-live="assertive">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Alert variant="destructive">
          <AlertTriangle className="size-4" />
          <AlertTitle>Error loading analytics</AlertTitle>
          <AlertDescription>
            Unable to load your health analytics. Please try again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Your health analytics overview</p>
        </div>
        <div className="flex items-center gap-2">
          {RANGE_OPTIONS.map((opt) => (
            <Button
              key={opt.value}
              variant={selectedRange === opt.value ? "default" : "outline"}
              size="sm"
              onClick={() => setRange(opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      {analyticsLoading && (
        <div className="space-y-4" role="status" aria-label="Loading dashboard data">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      )}

      {a && (
        <DashboardAnalyticsContent
          a={a}
          gridColor={gridColor}
          textColor={textColor}
          predictions={report?.predictions}
        />
      )}

      {!analyticsLoading && !a && !analyticsError && report && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              Analytics are being prepared. Check back after a few predictions.
            </p>
          </CardContent>
        </Card>
      )}

      {!analyticsLoading && !a && !analyticsError && !report && (
        <Card>
          <CardContent className="py-12 text-center space-y-4">
            <Stethoscope className="size-12 mx-auto text-muted-foreground" />
            <h3 className="text-lg font-semibold">Welcome to SymptomScope</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              Start by checking your symptoms. Your dashboard will populate with
              insights and trends over time.
            </p>
            <Link href="/symptom-checker">
              <Button>
                <Activity className="mr-2 size-4" />
                Check Symptoms
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}