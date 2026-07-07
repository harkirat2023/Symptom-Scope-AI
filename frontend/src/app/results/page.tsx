"use client";

import { Suspense, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export const dynamic = "force-dynamic";
import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Activity,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { predictSymptoms, type PredictionResponse } from "@/lib/api/predictions";
import { EmergencyActionPanel } from "@/components/features/emergency-action-panel";
import { DoctorRecommendationCard } from "@/components/features/doctor-recommendation-card";
import { cn } from "@/lib/utils";

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <Card className="max-w-md w-full mx-4">
            <CardContent className="py-12 text-center">
              <Activity className="size-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
              <p className="text-muted-foreground">Loading results...</p>
            </CardContent>
          </Card>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}

function ResultsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { userId, getToken } = useAuth();
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);

  const symptomsParam = searchParams.get("symptoms");
  const symptoms = symptomsParam ? symptomsParam.split(",") : [];

  const { isLoading, error } = useQuery({
    queryKey: ["prediction", symptomsParam],
    queryFn: async () => {
      if (!userId || !symptoms.length) return null;
      const token = await getToken();
      const result = await predictSymptoms({ symptoms }, token ?? undefined);
      setPrediction(result);
      return result;
    },
    enabled: !!userId && symptoms.length > 0 && !prediction,
  });

  const resultsRef = useRef<HTMLDivElement>(null);
  const errorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (prediction && resultsRef.current) {
      resultsRef.current.focus();
    }
  }, [prediction]);

  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.focus();
    }
  }, [error]);

  const severityColor: Record<string, string> = {
    Mild: "bg-success/10 text-success border-success/20",
    Moderate: "bg-warning/10 text-warning border-warning/20",
    Severe: "bg-destructive/10 text-destructive border-destructive/20",
  };

  if (!symptoms.length) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="py-12 text-center">
            <Activity className="size-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-semibold mb-2">No symptoms provided</h2>
            <p className="text-muted-foreground mb-6">
              Please use the Symptom Checker to get predictions.
            </p>
            <Button onClick={() => router.push("/symptom-checker")}>
              Go to Symptom Checker
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div id="main-content" className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <Button
          variant="ghost"
          onClick={() => router.push("/symptom-checker")}
          className="mb-6"
        >
          <ArrowLeft className="mr-2 size-4" />
          Back to Symptom Checker
        </Button>

        {isLoading && (
          <Card role="status" aria-live="polite" aria-label="Loading prediction results">
            <CardContent className="py-16 text-center">
              <div className="mx-auto mb-6 flex size-16 items-center justify-center rounded-full bg-primary/10">
                <RefreshCw className="size-8 animate-spin text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Loading Results
              </h3>
              <div className="space-y-3 max-w-sm mx-auto">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-5/6" />
              </div>
            </CardContent>
          </Card>
        )}

        {error && (
          <Alert ref={errorRef} tabIndex={-1} variant="destructive" role="alert" aria-live="assertive">
            <AlertTitle>Error loading results</AlertTitle>
            <AlertDescription>
              Unable to complete the analysis. Please try again.
            </AlertDescription>
          </Alert>
        )}

        {prediction && (
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

                <EmergencyActionPanel />
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
                        <div key={s.symptom} className="flex items-center gap-3">
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
          </motion.div>
        )}
      </div>
    </div>
  );
}
