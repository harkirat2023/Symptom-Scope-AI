"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Activity } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { cn } from "@/lib/utils";
import type { PredictionResponse } from "@/lib/api/predictions";
import { EmergencyActionPanel } from "@/components/features/emergency-action-panel";
import { DoctorRecommendationCard } from "@/components/features/doctor-recommendation-card";
import RiskCategoryBadge from "@/components/features/risk-score/risk-category-badge";

const severityColor: Record<string, string> = {
  Mild: "bg-success/10 text-success border-success/20",
  Moderate: "bg-warning/10 text-warning border-warning/20",
  Severe: "bg-destructive/10 text-destructive border-destructive/20",
};

interface PredictionResultsProps {
  prediction: PredictionResponse;
  onReset: () => void;
}

export function PredictionResults({ prediction, onReset }: PredictionResultsProps) {
  const router = useRouter();
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (resultsRef.current) {
      resultsRef.current.focus();
    }
  }, []);

  return (
    <motion.div
      ref={resultsRef}
      tabIndex={-1}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
      role="region"
      aria-live="polite"
      aria-label="Prediction results"
      aria-atomic="true"
    >
      {prediction.emergency.is_emergency && (
        <div className="rounded-xl border-2 border-destructive bg-destructive/5 p-4 shadow-lg ring-1 ring-destructive/30 sm:p-6">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-destructive/10 sm:size-12">
              <AlertTriangle className="size-5 text-destructive sm:size-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <h2 className="text-lg font-bold text-destructive sm:text-xl">
                Immediate Medical Attention Recommended
              </h2>
              <p className="mt-1 text-sm text-destructive/80 sm:text-base">
                {prediction.emergency.reasons.join(". ")}.
                Do not wait — seek emergency medical attention right now.
              </p>
            </div>
          </div>

          <EmergencyActionPanel predictedDisease={prediction.primary_prediction} />

          {prediction.emergency.explanation && (
            <p className="mt-3 text-xs text-muted-foreground">
              {prediction.emergency.explanation}
            </p>
          )}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {prediction.primary_prediction}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <p className="text-sm text-muted-foreground mb-1">
                Confidence
              </p>
              <p className="text-3xl font-bold text-primary">
                {prediction.confidence}%
              </p>
            </div>
            <div className="flex-1 min-w-[200px]">
              <p className="text-sm text-muted-foreground mb-1">
                Severity
              </p>
              <Badge
                className={cn(
                  "text-sm px-3 py-1",
                  severityColor[prediction.severity] ?? ""
                )}
              >
                {prediction.severity}
              </Badge>
            </div>
            {prediction.risk_score != null && (
              <div className="flex-1 min-w-[200px]">
                <p className="text-sm text-muted-foreground mb-1">
                  Health Risk Score
                </p>
                <div className="flex items-center gap-2">
                  <span className="text-3xl font-bold">
                    {prediction.risk_score}
                  </span>
                  <span className="text-sm text-muted-foreground">/ 100</span>
                  <RiskCategoryBadge
                    category={
                      (prediction.risk_category as "Low" | "Medium" | "High") ??
                      "Low"
                    }
                  />
                </div>
              </div>
            )}
          </div>

          {prediction.alternatives.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Alternative possibilities
              </p>
              <div className="flex flex-wrap gap-2">
                {prediction.alternatives.map((alt) => (
                  <Badge key={alt} variant="outline">
                    {alt}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {prediction.top_contributing_symptoms.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Top contributing symptoms
              </p>
              <div className="space-y-2">
                {prediction.top_contributing_symptoms.map((s) => (
                  <div
                    key={s.symptom}
                    className="flex items-center gap-3"
                  >
                    <span className="text-sm flex-1">
                      {s.symptom.replace(/_/g, " ")}
                    </span>
                    <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{
                          width: `${Math.min(s.importance * 100, 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {prediction.precautions.length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Recommended precautions
              </p>
              <ul className="space-y-1">
                {prediction.precautions.map((p, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm"
                  >
                    <span className="mt-1 size-1.5 rounded-full bg-primary shrink-0" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {prediction.doctor_recommendations.length > 0 && (
        <div>
          <h3 className="mb-3 text-lg font-semibold">
            Recommended Doctors
          </h3>
          <div className="space-y-3">
            {prediction.doctor_recommendations.map((doctor) => (
              <DoctorRecommendationCard key={doctor.name} doctor={doctor} />
            ))}
          </div>
        </div>
      )}

      <Alert variant="default" className="border-amber-500/30 bg-amber-500/5">
        <AlertTriangle className="size-4 text-amber-500" />
        <AlertTitle className="text-amber-700 dark:text-amber-400">Medical Disclaimer</AlertTitle>
        <AlertDescription>
          This assessment is for informational purposes only and does not constitute
          a medical diagnosis. Please consult a healthcare professional.
        </AlertDescription>
      </Alert>

      <div className="flex justify-center gap-4">
        <Button variant="outline" onClick={onReset}>
          Check New Symptoms
        </Button>
        <Button onClick={() => router.push("/dashboard")}>
          <Activity className="mr-2 size-4" />
          Go to Dashboard
        </Button>
      </div>
    </motion.div>
  );
}
