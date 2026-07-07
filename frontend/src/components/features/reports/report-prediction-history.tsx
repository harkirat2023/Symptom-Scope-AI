"use client";

import { BrainCircuit } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ReportResponse } from "@/lib/api/predictions";

interface ReportPredictionHistoryProps {
  report: ReportResponse;
}

export function ReportPredictionHistory({ report }: ReportPredictionHistoryProps) {
  if (!report.predictions || report.predictions.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <BrainCircuit className="size-4 text-primary" />
          Prediction History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="max-h-80">
          <div className="space-y-2">
            {report.predictions.map((p) => (
              <div key={p.id} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">{p.prediction}</p>
                    <Badge variant={p.severity === "Severe" ? "destructive" : "outline"} className="text-xs">
                      {p.severity}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {new Date(p.timestamp).toLocaleDateString("en-US", {
                      year: "numeric", month: "short", day: "numeric",
                    })}
                    {" · "}{p.confidence}% confidence
                  </p>
                </div>
                <div className="flex flex-wrap gap-1 ml-3">
                  {p.symptoms.slice(0, 3).map((s) => (
                    <Badge key={s} variant="secondary" className="text-xs">{s}</Badge>
                  ))}
                  {p.symptoms.length > 3 && (
                    <Badge variant="outline" className="text-xs">+{p.symptoms.length - 3}</Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
