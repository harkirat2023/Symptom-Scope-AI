"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { RiskScoreHistoryItem } from "@/lib/api/risk-score";
import RiskCategoryBadge from "./risk-category-badge";

export default function RiskTrendChart({
  data,
  gridColor = "#e5e7eb",
  textColor = "#6b7280",
}: {
  data: RiskScoreHistoryItem[];
  gridColor?: string;
  textColor?: string;
}) {
  const chartData = useMemo(() => {
    return data
      .slice()
      .reverse()
      .map((d) => ({
        ...d,
        label: new Date(d.timestamp).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        }),
      }));
  }, [data]);

  if (chartData.length === 0) {
    return (
      <div className="rounded-lg border p-4 text-center text-sm text-muted-foreground">
        No history data available yet.
      </div>
    );
  }

  return (
    <div className="rounded-lg border p-4">
      <h3 className="mb-3 text-sm font-semibold">Score Trend</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: textColor }}
            axisLine={{ stroke: gridColor }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: textColor }}
            axisLine={{ stroke: gridColor }}
          />
          <Tooltip
            contentStyle={{
              fontSize: 12,
              borderRadius: 8,
              border: "1px solid #e5e7eb",
            }}
            formatter={(value) => [`${value}`, "Score"]}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ r: 3, fill: "#6366f1" }}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-2 flex flex-wrap gap-2">
        {chartData.slice(0, 5).map((d, i) => (
          <div
            key={i}
            className="flex items-center gap-1 text-xs text-muted-foreground"
          >
            <span>{d.label}:</span>
            <RiskCategoryBadge
              category={d.category as "Low" | "Medium" | "High"}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
