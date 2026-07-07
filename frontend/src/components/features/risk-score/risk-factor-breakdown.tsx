"use client";

import type { RiskFactorBreakdown as RB } from "@/lib/api/risk-score";

const FACTORS: {
  key: keyof RB;
  label: string;
  max: number;
  color: string;
}[] = [
  { key: "age_score", label: "Age", max: 15, color: "#6366f1" },
  { key: "bmi_score", label: "BMI", max: 10, color: "#8b5cf6" },
  { key: "lifestyle_score", label: "Lifestyle", max: 10, color: "#a855f7" },
  { key: "smoking_score", label: "Smoking", max: 15, color: "#ec4899" },
  { key: "sleep_score", label: "Sleep", max: 10, color: "#14b8a6" },
  {
    key: "existing_conditions_score",
    label: "Existing Conditions",
    max: 20,
    color: "#f97316",
  },
  {
    key: "prediction_history_score",
    label: "Prediction History",
    max: 20,
    color: "#06b6d4",
  },
  {
    key: "severity_trend_score",
    label: "Severity Trend",
    max: 10,
    color: "#e11d48",
  },
];

export default function RiskFactorBreakdown({
  breakdown,
}: {
  breakdown: RB;
}) {
  return (
    <div className="rounded-lg border p-4">
      <h3 className="mb-3 text-sm font-semibold">Factor Breakdown</h3>
      <div className="space-y-3">
        {FACTORS.map((factor) => {
          const value = breakdown[factor.key] ?? 0;
          const pct = factor.max > 0 ? (value / factor.max) * 100 : 0;
          return (
            <div key={factor.key}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-muted-foreground">{factor.label}</span>
                <span className="font-medium">
                  {value}/{factor.max}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: factor.color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
