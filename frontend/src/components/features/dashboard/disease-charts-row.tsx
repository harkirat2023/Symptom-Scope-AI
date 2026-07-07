"use client";

import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CustomTooltip } from "@/components/shared/custom-tooltip";
import { severityColors, SEVERITY_ORDER } from "@/components/shared/dashboard-types";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface DiseaseChartsRowProps {
  a: AnalyticsResponse;
  gridColor: string;
  textColor: string;
}

export function DiseaseChartsRow({ a, gridColor, textColor }: DiseaseChartsRowProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Disease Frequency</CardTitle>
          </CardHeader>
          <CardContent>
            {a.disease_frequency.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={a.disease_frequency.slice(0, 6)}
                    layout="vertical"
                    margin={{ top: 0, right: 20, left: 0, bottom: 0 }}
                    barCategoryGap="20%"
                  >
                    <CartesianGrid stroke={gridColor} strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" tick={{ fill: textColor, fontSize: 12 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                    <YAxis
                      type="category"
                      dataKey="disease"
                      tick={{ fill: textColor, fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      width={120}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="var(--color-primary)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data for this period.</p>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Severity Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            {a.severity_breakdown.length > 0 ? (
              <div className="flex items-center h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={a.severity_breakdown.map((s) => ({
                        name: s.severity,
                        value: s.count,
                      }))}
                      cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                      paddingAngle={3} dataKey="value"
                    >
                      {a.severity_breakdown.map((entry) => (
                        <Cell key={entry.severity} fill={severityColors[entry.severity] ?? "#94a3b8"} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="shrink-0 space-y-3">
                  {SEVERITY_ORDER.filter((sev) =>
                    a.severity_breakdown.some((s) => s.severity === sev)
                  ).map((sev) => {
                    const item = a.severity_breakdown.find((s) => s.severity === sev);
                    return (
                      <div key={sev} className="flex items-center gap-2">
                        <div className="size-3 rounded-full" style={{ backgroundColor: severityColors[sev] }} />
                        <span className="text-sm">{sev}</span>
                        <span className="text-sm text-muted-foreground">
                          {item?.count} ({item?.percentage}%)
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data for this period.</p>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
