"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";

export const dynamic = "force-dynamic";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { predictSymptoms, type PredictionResponse } from "@/lib/api/predictions";
import { symptomFormSchema, type SymptomFormValues } from "@/lib/validations/symptom-form";
import { StepIndicator, type CheckerStep } from "@/components/features/step-indicator";
import { SymptomSelectionStep } from "@/components/features/symptom-selection-step";
import { DetailsStep } from "@/components/features/details-step";
import { AnalyzingStep } from "@/components/features/analyzing-step";
import { PredictionResults } from "@/components/features/prediction-results";

export default function SymptomCheckerPage() {
  const { userId, getToken } = useAuth();

  const [step, setStep] = useState<CheckerStep>("symptoms");
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stepRef = useRef<HTMLDivElement>(null);
  const errorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (stepRef.current) {
      stepRef.current.focus();
    }
  }, [step]);

  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.focus();
    }
  }, [error]);

  const form = useForm<SymptomFormValues>({
    resolver: zodResolver(symptomFormSchema),
    defaultValues: {
      symptoms: [],
      age: null,
      gender: null,
      existingConditions: [],
      symptomDuration: "",
      painLevel: null,
    },
  });

  const { register, control, formState: { errors }, getValues, reset } = form;

  const predictMutation = useMutation({
    mutationFn: async (input: {
      symptoms: string[];
      age?: number | null;
      gender?: string | null;
      existing_conditions?: string[];
      symptom_duration?: string;
      pain_level?: number | null;
    }) => {
      const token = await getToken();
      return predictSymptoms(input, token ?? undefined);
    },
    onSuccess: (data) => {
      setPrediction(data);
      setStep("results");
    },
    onError: (err: Error) => {
      setError(err.message);
      setStep("symptoms");
    },
  });

  const handleStartAnalysis = async () => {
    if (!userId) return;
    const isValid = await form.trigger();
    if (!isValid) return;
    setStep("analyzing");
    setError(null);
    const values = getValues();
    predictMutation.mutate({
      symptoms: values.symptoms,
      age: values.age,
      gender: values.gender,
      existing_conditions: values.existingConditions,
      symptom_duration: values.symptomDuration || undefined,
      pain_level: values.painLevel,
    });
  };

  const handleReset = () => {
    reset();
    setPrediction(null);
    setError(null);
    setStep("symptoms");
  };

  return (
    <div className="min-h-screen bg-background">
      <div id="main-content" className="mx-auto w-full max-w-none px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">Symptom Checker</h1>
          <p className="mt-2 text-muted-foreground">
            Describe your symptoms for an AI-powered health assessment
          </p>
        </div>

        <StepIndicator current={step} />

        <Alert variant="default" className="mb-6 border-amber-500/30 bg-amber-500/5">
          <AlertTriangle className="size-4 text-amber-500" />
          <AlertTitle className="text-amber-700 dark:text-amber-400">Medical Disclaimer</AlertTitle>
          <AlertDescription>
            This tool provides an AI-generated assessment and is not a medical diagnosis.
            Always consult a qualified healthcare professional for medical advice.
          </AlertDescription>
        </Alert>

        <AnimatePresence mode="wait">
          {step === "symptoms" && (
            <motion.div
              key="symptoms"
              ref={stepRef}
              tabIndex={-1}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <SymptomSelectionStep
                control={control}
                onComplete={() => setStep("details")}
              />
            </motion.div>
          )}

          {step === "details" && (
            <motion.div
              key="details"
              ref={stepRef}
              tabIndex={-1}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <DetailsStep
                register={register}
                errors={errors}
                control={control}
                onBack={() => setStep("symptoms")}
                onStartAnalysis={handleStartAnalysis}
              />
            </motion.div>
          )}

          {step === "analyzing" && (
            <motion.div
              key="analyzing"
              ref={stepRef}
              tabIndex={-1}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              role="status"
              aria-live="polite"
            >
              <AnalyzingStep />
            </motion.div>
          )}

          {step === "results" && prediction && (
            <PredictionResults prediction={prediction} onReset={handleReset} />
          )}
        </AnimatePresence>

        {error && (
          <Alert ref={errorRef} tabIndex={-1} variant="destructive" className="mt-4" role="alert" aria-live="assertive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              {error}. Please try again or check your connection.
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  );
}
