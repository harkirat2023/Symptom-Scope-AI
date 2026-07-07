"use client";

import { Activity, AlertTriangle, TrendingUp, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface SummaryCardsProps {
  summary: AnalyticsResponse["summary"] | undefined;
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-2 lg:grid-cols-4 gap-4"
    >
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10">
              <Activity className="size-5 text-primary" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-muted-foreground">Total Checks</p>
              <p className="text-xl font-semibold">{summary?.total_predictions ?? 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-teal-500/10">
              <BarChart3 className="size-5 text-teal-500" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-muted-foreground">Unique Conditions</p>
              <p className="text-xl font-semibold">{summary?.unique_conditions ?? 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-warning/10">
              <TrendingUp className="size-5 text-warning" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-muted-foreground">Avg Confidence</p>
              <p className="text-xl font-semibold">{summary?.average_confidence ?? 0}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-destructive/10">
              <AlertTriangle className="size-5 text-destructive" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-muted-foreground">Severe Episodes</p>
              <p className="text-xl font-semibold">{summary?.severe_count ?? 0}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
