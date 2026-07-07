"use client";

import { motion } from "framer-motion";
import { HeartPulse } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { HealthSummary } from "@/lib/api/predictions";

interface HealthSummaryStripProps {
  healthSummary: HealthSummary;
}

export function HealthSummaryStrip({ healthSummary }: HealthSummaryStripProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <Card className={cn(
        "border-l-4",
        healthSummary.risk_level === "high" && "border-l-destructive",
        healthSummary.risk_level === "moderate" && "border-l-warning",
        healthSummary.risk_level === "low" && "border-l-success"
      )}>
        <CardContent className="p-4 flex items-start gap-4">
          <div className={cn(
            "flex size-10 items-center justify-center rounded-lg shrink-0",
            healthSummary.risk_level === "high" && "bg-destructive/10",
            healthSummary.risk_level === "moderate" && "bg-warning/10",
            healthSummary.risk_level === "low" && "bg-success/10"
          )}>
            <HeartPulse className={cn(
              "size-5",
              healthSummary.risk_level === "high" && "text-destructive",
              healthSummary.risk_level === "moderate" && "text-warning",
              healthSummary.risk_level === "low" && "text-success"
            )} />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-sm">
                Health Summary ({healthSummary.period_label})
              </h3>
              <Badge variant={
                healthSummary.risk_level === "high" ? "destructive" :
                healthSummary.risk_level === "moderate" ? "outline" :
                "secondary"
              } className="text-xs">
                {healthSummary.risk_level === "high" ? "High Risk" :
                 healthSummary.risk_level === "moderate" ? "Moderate" : "Low Risk"}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {healthSummary.summary_text}
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
