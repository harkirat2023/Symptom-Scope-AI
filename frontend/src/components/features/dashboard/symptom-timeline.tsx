"use client";

import { motion } from "framer-motion";
import { Calendar, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { severityBadgeColors } from "@/components/shared/dashboard-types";
import type { PredictionRecord } from "@/lib/api/predictions";

interface SymptomTimelineProps {
  predictions: PredictionRecord[];
}

export function SymptomTimeline({ predictions }: SymptomTimelineProps) {
  if (predictions.length === 0) return null;

  const sortedPredictions = [...predictions].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Calendar className="size-4 text-primary" />
            Symptom Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="max-h-80">
            <div className="relative space-y-0">
              {sortedPredictions.map((record, idx) => (
                <div key={record.id} className="flex gap-4 pb-6 relative">
                  {idx < sortedPredictions.length - 1 && (
                    <div className="absolute left-[11px] top-6 bottom-0 w-0.5 bg-border" />
                  )}
                  <div className="flex shrink-0 items-start pt-1">
                    <div
                      className={cn(
                        "size-5 rounded-full border-2 flex items-center justify-center",
                        record.severity === "Severe"
                          ? "border-destructive bg-destructive/10"
                          : record.severity === "Moderate"
                          ? "border-warning bg-warning/10"
                          : "border-success bg-success/10"
                      )}
                    >
                      <Activity className="size-2.5 text-foreground" />
                    </div>
                  </div>
                  <div className="min-w-0 flex-1 space-y-1.5">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs text-muted-foreground">
                        {new Date(record.timestamp).toLocaleDateString("en-US", {
                          month: "short", day: "numeric", year: "numeric",
                        })}
                      </span>
                      <Badge
                        className={cn(
                          "text-[10px] px-1.5 py-0",
                          severityBadgeColors[record.severity] ?? ""
                        )}
                      >
                        {record.severity}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {record.symptoms.map((symptom) => (
                        <Badge key={symptom} variant="outline" className="text-[10px]">
                          {symptom}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Predicted: <span className="font-medium text-foreground">{record.prediction}</span>
                      {" · "}{record.confidence}% confidence
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}
