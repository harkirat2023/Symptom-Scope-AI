"use client";

import { motion } from "framer-motion";
import { Calendar } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AnalyticsResponse } from "@/lib/api/predictions";

interface RecurringConditionsProps {
  recurringConditions: AnalyticsResponse["recurring_conditions"];
}

export function RecurringConditions({ recurringConditions }: RecurringConditionsProps) {
  if (recurringConditions.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.45 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Calendar className="size-4 text-warning" />
            Recurring Conditions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recurringConditions.slice(0, 5).map((rc) => (
              <div key={rc.disease} className="flex items-center justify-between p-3 rounded-lg border">
                <div>
                  <p className="text-sm font-medium">{rc.disease}</p>
                  <p className="text-xs text-muted-foreground">
                    {rc.occurrences} {rc.occurrences === 1 ? "occurrence" : "occurrences"}
                    {" · "}Last: {new Date(rc.last_detected).toLocaleDateString()}
                  </p>
                </div>
                <Badge variant={
                  rc.frequency === "frequent" ? "destructive" :
                  rc.frequency === "occasional" ? "outline" : "secondary"
                } className="text-xs">
                  {rc.frequency}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
