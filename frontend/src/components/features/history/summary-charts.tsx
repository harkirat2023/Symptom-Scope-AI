"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CustomTooltip } from "@/components/shared/custom-tooltip";

const severityChartColors: Record<string, string> = {
  Mild: "#22c55e",
  Moderate: "#f59e0b",
  Severe: "#ef4444",
};

interface SummaryChartsProps {
  conditionCounts: { name: string; value: number }[];
  severityCounts: { name: string; value: number }[];
  symptomClusters: { name: string; value: number }[];
  gridColor: string;
  textColor: string;
}

export function SummaryCharts({ conditionCounts, severityCounts, symptomClusters, gridColor, textColor }: SummaryChartsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {conditionCounts.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Conditions</CardTitle></CardHeader>
          <CardContent>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={conditionCounts} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }} barCategoryGap="25%">
                  <CartesianGrid stroke={gridColor} strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fill: textColor, fontSize: 10 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: textColor, fontSize: 10 }} axisLine={false} tickLine={false} width={90} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" fill="var(--color-primary)" radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
      {severityCounts.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Severity Breakdown</CardTitle></CardHeader>
          <CardContent>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityCounts} margin={{ top: 0, right: 10, left: 0, bottom: 0 }} barCategoryGap="30%">
                  <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fill: textColor, fontSize: 10 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                  <YAxis tick={{ fill: textColor, fontSize: 10 }} axisLine={{ stroke: gridColor }} tickLine={false} allowDecimals={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                    {severityCounts.map((entry) => (
                      <Cell key={entry.name} fill={severityChartColors[entry.name] ?? "var(--color-primary)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
      {symptomClusters.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Most Frequent Symptoms</CardTitle></CardHeader>
          <CardContent>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={symptomClusters} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }} barCategoryGap="25%">
                  <CartesianGrid stroke={gridColor} strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fill: textColor, fontSize: 10 }} axisLine={{ stroke: gridColor }} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: textColor, fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" fill="#14b8a6" radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
