"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CustomTooltip } from "@/components/shared/custom-tooltip";
import { severityColors } from "@/components/shared/dashboard-types";
import type { ReportResponse, AnalyticsResponse } from "@/lib/api/predictions";

interface ReportChartsProps {
  report: ReportResponse;
  analytics: AnalyticsResponse | undefined;
  gridColor: string;
  textColor: string;
}

export function ReportCharts({ report, analytics, gridColor, textColor }: ReportChartsProps) {
  const severityDistribution = report.severity_distribution
    ? Object.entries(report.severity_distribution).map(([severity, count]) => ({
        name: severity,
        value: count,
      }))
    : [];

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {severityDistribution.length > 0 && (
          <Card>
            <CardHeader><CardTitle className="text-base">Severity Distribution</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center h-64">
                <ResponsiveContainer width="60%" height="100%">
                  <PieChart>
                    <Pie
                      data={severityDistribution}
                      cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                      paddingAngle={3} dataKey="value"
                    >
                      {severityDistribution.map((entry) => (
                        <Cell key={entry.name} fill={severityColors[entry.name] ?? "#94a3b8"} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-3">
                  {severityDistribution.map((entry) => (
                    <div key={entry.name} className="flex items-center gap-2">
                      <div className="size-3 rounded-full" style={{ backgroundColor: severityColors[entry.name] ?? "#94a3b8" }} />
                      <span className="text-sm">{entry.name}</span>
                      <span className="text-sm text-muted-foreground">{entry.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        {analytics?.confidence_trends && analytics.confidence_trends.length >= 2 && (
          <Card>
            <CardHeader><CardTitle className="text-base">Confidence Over Time</CardTitle></CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={analytics.confidence_trends} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                    <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                    <YAxis domain={[0, 100]} tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} unit="%" />
                    <Tooltip content={<CustomTooltip />} />
                    <Line type="monotone" dataKey="average_confidence" name="Avg Confidence" stroke="var(--color-primary)" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {analytics && analytics.disease_trends.length >= 2 && (
        <Card>
          <CardHeader><CardTitle className="text-base">Check-Up Trend Analysis</CardTitle></CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={analytics.disease_trends.map((t) => ({ month: t.month, total: t.total }))}
                  margin={{ top: 5, right: 10, left: -10, bottom: 0 }} barCategoryGap="30%"
                >
                  <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                  <YAxis tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} allowDecimals={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="total" fill="var(--color-primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
}
