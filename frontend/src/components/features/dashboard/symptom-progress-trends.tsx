"use client";

import { motion } from "framer-motion";
import { BrainCircuit } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendIcon } from "@/components/shared/trend-icon";
import { cn } from "@/lib/utils";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface SymptomProgressTrendsProps {
  symptomTrends: AnalyticsResponse["symptom_trends"];
}

export function SymptomProgressTrends({ symptomTrends }: SymptomProgressTrendsProps) {
  if (symptomTrends.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <BrainCircuit className="size-4 text-primary" />
            Symptom Progression Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {symptomTrends.slice(0, 9).map((st) => (
              <div key={st.symptom} className="flex items-center gap-3 p-3 rounded-lg border bg-card">
                <div className={cn(
                  "flex size-8 items-center justify-center rounded-full",
                  st.direction === "increasing" && "bg-destructive/10",
                  st.direction === "decreasing" && "bg-success/10",
                  st.direction === "stable" && "bg-muted",
                  st.direction === "insufficient_data" && "bg-muted",
                )}>
                  <TrendIcon direction={st.direction} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">{st.symptom}</p>
                  <div className="flex items-center gap-1.5">
                    <span className={cn(
                      "text-xs",
                      st.direction === "increasing" && "text-destructive",
                      st.direction === "decreasing" && "text-success",
                      st.direction === "stable" && "text-muted-foreground",
                      st.direction === "insufficient_data" && "text-muted-foreground",
                    )}>
                      {st.direction === "increasing" && `+${st.change_pct}%`}
                      {st.direction === "decreasing" && `${st.change_pct}%`}
                      {st.direction === "stable" && "Stable"}
                      {st.direction === "insufficient_data" && "Limited data"}
                    </span>
                    {st.data.length > 0 && (
                      <span className="text-xs text-muted-foreground">
                        ({st.data[st.data.length - 1]?.count ?? 0} recent)
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
