"use client";

import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CustomTooltip } from "@/components/shared/custom-tooltip";
import { severityColors, SEVERITY_ORDER } from "@/components/shared/dashboard-types";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface TrendChartsRowProps {
  a: AnalyticsResponse;
  gridColor: string;
  textColor: string;
}

export function TrendChartsRow({ a, gridColor, textColor }: TrendChartsRowProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {a.disease_trends.length >= 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Check-Ups Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={a.disease_trends.map((t) => ({
                      month: t.month,
                      Total: t.total,
                    }))}
                    margin={{ top: 5, right: 10, left: -10, bottom: 0 }}
                  >
                    <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                    <YAxis tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} allowDecimals={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="Total" stroke="var(--color-primary)" fill="var(--color-primary)" fillOpacity={0.15} strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {a.severity_trends.length >= 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Severity Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={a.severity_trends.map((t) => {
                      const row: Record<string, string | number> = { month: t.month };
                      for (const b of t.breakdown) {
                        row[b.severity] = b.count;
                      }
                      return row;
                    })}
                    margin={{ top: 5, right: 10, left: -10, bottom: 0 }}
                    barCategoryGap="20%"
                    stackOffset="sign"
                  >
                    <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                    <YAxis tick={{ fill: textColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickLine={false} allowDecimals={false} />
                    <Tooltip content={<CustomTooltip />} />
                    {SEVERITY_ORDER.filter((sev) =>
                      a.severity_trends.some((t) => t.breakdown.some((b) => b.severity === sev))
                    ).map((sev) => (
                      <Bar key={sev} dataKey={sev} stackId="severity" fill={severityColors[sev] ?? "#94a3b8"} radius={[2, 2, 0, 0]} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
