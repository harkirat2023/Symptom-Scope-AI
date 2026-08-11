"use client";

import { Suspense, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Activity,
  ArrowLeft,
  RefreshCw,
  HeartPulse,
  Clock,
  Utensils,
  Droplets,
  Moon,
  Dumbbell,
  Shield,
  AlertCircle,
  Stethoscope,
  CheckCircle,
  XCircle,
  Brain,
  ListTodo,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getLatestRecoveryPlan, getLatestPrediction, generateRecoveryPlan, regenerateRecoveryPlan, type RecoveryPlanResponse } from "@/lib/api/recovery";

export default function RecoveryPlanPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <Card className="max-w-md w-full mx-4">
            <CardContent className="py-12 text-center">
              <Activity className="size-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
              <p className="text-muted-foreground">Loading recovery plan...</p>
            </CardContent>
          </Card>
        </div>
      }
    >
      <RecoveryPlanContent />
    </Suspense>
  );
}

function RecoveryPlanContent() {
  const router = useRouter();
  const { userId, getToken } = useAuth();
  const queryClient = useQueryClient();
  const [prediction, setPrediction] = useState<{ primary_prediction: string; confidence: number; severity: string; prediction_id: string } | null>(null);
  const [generatedPlan, setGeneratedPlan] = useState<RecoveryPlanResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

// Fetch latest prediction
  const { isLoading: predictionLoading } = useQuery({
    queryKey: ["latest-prediction", userId],
    queryFn: async () => {
      if (!userId) return null;
      const token = await getToken();
      const result = await getLatestPrediction(token ?? undefined);
      if (result) setPrediction(result);
      return result;
    },
    enabled: !!userId,
  });

  // Fetch existing recovery plan
  const { data: recoveryPlan } = useQuery({
    queryKey: ["recovery-plan", userId],
    queryFn: async () => {
      if (!userId) return null;
      const token = await getToken();
      return getLatestRecoveryPlan(token ?? undefined);
    },
    enabled: !!userId && !!prediction,
  });

  // Generate recovery plan mutation
  const generateMutation = useMutation({
    mutationFn: async (predictionId: string) => {
      if (!userId) throw new Error("Not authenticated");
      const token = await getToken();
      return generateRecoveryPlan(predictionId, token ?? undefined);
    },
    onSuccess: (data) => {
      setGeneratedPlan(data);
      setIsGenerating(false);
      queryClient.invalidateQueries({ queryKey: ["recovery-plan", userId] });
    },
    onError: (err: Error) => {
      setError(err.message);
      setIsGenerating(false);
    },
  });

  // Regenerate mutation
  const regenerateMutation = useMutation({
    mutationFn: async (planId: string) => {
      if (!userId) throw new Error("Not authenticated");
      const token = await getToken();
      return regenerateRecoveryPlan(planId, token ?? undefined);
    },
    onSuccess: (data) => {
      setGeneratedPlan(data);
      queryClient.invalidateQueries({ queryKey: ["recovery-plan", userId] });
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const planToShow = generatedPlan || recoveryPlan;

  const handleGenerate = async () => {
    if (!prediction) return;
    setIsGenerating(true);
    setError(null);
    await generateMutation.mutateAsync(prediction.prediction_id);
  };

  const handleRegenerate = async () => {
    if (!planToShow) return;
    setError(null);
    await regenerateMutation.mutateAsync(planToShow.id);
  };

  // No prediction exists
  if (!prediction && !predictionLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div id="main-content" className="mx-auto w-full max-w-none px-4 py-8 sm:px-6 lg:px-8">
          <Card>
            <CardContent className="py-12 text-center space-y-6">
              <HeartPulse className="size-12 mx-auto text-muted-foreground" />
              <h2 className="text-xl font-semibold">No Prediction Found</h2>
              <p className="text-muted-foreground max-w-md mx-auto">
                Complete a symptom assessment first to generate a personalized recovery plan.
              </p>
              <Button onClick={() => router.push("/symptom-checker")} size="lg">
                <Activity className="mr-2 size-4" />
                Start Symptom Checker
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Loading prediction
  if (predictionLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div id="main-content" className="mx-auto w-full max-w-none px-4 py-8 sm:px-6 lg:px-8">
          <Card>
            <CardContent className="py-12 text-center">
              <Activity className="size-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
              <p className="text-muted-foreground">Loading your latest prediction...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div id="main-content" className="mx-auto w-full max-w-none px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Recovery Plan</h1>
            <p className="text-muted-foreground">
              Personalized recovery guidance for {prediction?.primary_prediction}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={() => router.push("/results")} disabled={!prediction}>
              <ArrowLeft className="mr-2 size-4" />
              Back to Results
            </Button>
            {!planToShow && !isGenerating && !generateMutation.isPending && (
              <Button onClick={handleGenerate} size="lg">
                <RefreshCw className="mr-2 size-4" />
                Generate Recovery Plan
              </Button>
            )}
            {planToShow && !regenerateMutation.isPending && (
              <Button variant="outline" onClick={handleRegenerate}>
                <RefreshCw className="mr-2 size-4" />
                Regenerate
              </Button>
            )}
          </div>
        </div>

        {/* Disease Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <HeartPulse className="text-primary" />
              Disease Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <p className="text-sm text-muted-foreground mb-1">Condition</p>
                <p className="text-2xl font-bold">{prediction?.primary_prediction}</p>
              </div>
              <div className="flex-1 min-w-[200px]">
                <p className="text-sm text-muted-foreground mb-1">Confidence</p>
                <p className="text-2xl font-bold text-primary">{prediction?.confidence}%</p>
              </div>
              <div className="flex-1 min-w-[200px]">
                <p className="text-sm text-muted-foreground mb-1">Severity</p>
                <Badge variant="outline" className="text-sm px-3 py-1">
                  {prediction?.severity}
                </Badge>
              </div>
            </div>
            <Alert variant="default" className="border-amber-500/30 bg-amber-500/5">
              <AlertTriangle className="size-4 text-amber-500" />
              <AlertTitle className="text-amber-700 dark:text-amber-400">Medical Disclaimer</AlertTitle>
              <AlertDescription>
                This recovery plan is for educational purposes only and does not constitute medical advice.
                Always consult a qualified healthcare professional for medical concerns, diagnosis, or treatment.
                In case of emergency, contact emergency services immediately.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* Recovery Plan Content */}
        {isGenerating || generateMutation.isPending ? (
          <Card role="status" aria-live="polite" aria-label="Generating recovery plan">
            <CardContent className="py-16 text-center">
              <div className="mx-auto mb-6 flex size-16 items-center justify-center rounded-full bg-primary/10">
                <RefreshCw className="size-8 animate-spin text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Generating Your Recovery Plan</h3>
              <div className="space-y-3 max-w-sm mx-auto">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-5/6" />
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                Our AI is creating a personalized recovery plan based on your prediction.
              </p>
            </CardContent>
          </Card>
        ) : planToShow ? (
          <ScrollArea className="h-[calc(100vh-300px)] min-h-[400px]">
            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="diet">Diet & Lifestyle</TabsTrigger>
                <TabsTrigger value="warning">Warnings</TabsTrigger>
              </TabsList>

              <TabsContent value="overview">
                <div className="space-y-6">
                  {/* Recovery Timeline */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="text-primary" />
                        Recovery Timeline
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {planToShow.recovery_timeline.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex items-start gap-4 p-4 bg-muted/50 rounded-lg"
                          >
                            <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                              <span className="font-semibold">{index + 1}</span>
                            </div>
                            <p className="text-sm pt-1">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Foods to Eat */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <CheckCircle className="text-green-500" />
                        Foods to Eat
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.foods_to_eat.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg"
                          >
                            <CheckCircle className="size-5 text-green-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Foods to Avoid */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <XCircle className="text-red-500" />
                        Foods to Avoid
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.foods_to_avoid.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="flex items-start gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg"
                          >
                            <XCircle className="size-5 text-red-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Hydration */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Droplets className="text-blue-500" />
                        Hydration Advice
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">{planToShow.hydration_advice}</p>
                    </CardContent>
                  </Card>

                  {/* Sleep */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Moon className="text-purple-500" />
                        Sleep Recommendation
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">{planToShow.sleep_recommendation}</p>
                    </CardContent>
                  </Card>

                  {/* Exercise */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Dumbbell className="text-orange-500" />
                        Exercise & Physical Activity
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm">{planToShow.exercise_recommendation}</p>
                      <Separator />
                      <div>
                        <p className="text-sm font-medium mb-2">Daily Activities</p>
                        <div className="space-y-2">
                          {planToShow.daily_physical_activity.map((item, index) => (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: index * 0.05 }}
                              className="flex items-center gap-2 p-2 bg-muted/50 rounded"
                            >
                              <Activity className="size-4 text-primary" />
                              <p className="text-sm">{item}</p>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Lifestyle Changes */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="text-indigo-500" />
                        Lifestyle Changes
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.lifestyle_changes.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="flex items-start gap-2 p-2 bg-muted/50 rounded"
                          >
                            <Shield className="size-4 text-indigo-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recovery Checklist */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <ListTodo className="text-primary" />
                        Daily Recovery Checklist
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.recovery_checklist.map((item, index) => (
                          <motion.label
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="flex items-center gap-2 cursor-pointer p-2 bg-muted/50 rounded hover:bg-muted"
                          >
                            <input type="checkbox" className="size-4 accent-primary" />
                            <p className="text-sm">{item}</p>
                          </motion.label>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Progress Tracker */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="text-primary" />
                        Progress Tracker
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(planToShow.progress_tracker || {}).map(([week, goals]) => (
                          <div key={week} className="p-3 bg-muted/50 rounded-lg">
                            <p className="font-medium capitalize">{week.replace("_", " ")}</p>
                            <p className="text-sm text-muted-foreground mt-1">{String(goals)}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="diet">
                <div className="space-y-6">
                  {/* Diet Recommendations */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Utensils className="text-primary" />
                        Diet Recommendations
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="p-3 bg-muted/50 rounded-lg">
                        <p className="font-medium">General Principles</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          {String(planToShow.diet_recommendations?.general_principles || "Eat a balanced diet rich in fruits, vegetables, lean proteins, and whole grains.")}
                        </p>
                      </div>
                      <div className="p-3 bg-muted/50 rounded-lg">
                        <p className="font-medium">Key Nutrients</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          {String(planToShow.diet_recommendations?.specific_nutrients || "Focus on vitamins C, D, zinc, and antioxidants for immune support.")}
                        </p>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Foods to Eat */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <CheckCircle className="text-green-500" />
                        Recommended Foods
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.foods_to_eat.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg"
                          >
                            <CheckCircle className="size-5 text-green-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Foods to Avoid */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <XCircle className="text-red-500" />
                        Foods to Limit or Avoid
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.foods_to_avoid.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-start gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg"
                          >
                            <XCircle className="size-5 text-red-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="warning">
                <div className="space-y-6">
                  {/* When to Visit Doctor */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Stethoscope className="text-blue-500" />
                        When to Visit a Doctor
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.when_to_visit_doctor.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
                          >
                            <Stethoscope className="size-4 text-blue-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Emergency Warning Signs */}
                  <Card className="border-destructive/30 bg-destructive/5">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertCircle className="text-destructive" />
                        Emergency Warning Signs
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Alert variant="destructive" className="mb-4">
                        <AlertCircle className="size-4" />
                        <AlertTitle>Seek immediate medical attention if you experience any of these:</AlertTitle>
                      </Alert>
                      <div className="space-y-2">
                        {planToShow.emergency_warning_signs.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg"
                          >
                            <AlertCircle className="size-4 text-destructive shrink-0 mt-0.5" />
                            <p className="text-sm font-medium">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Mental Wellness */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Brain className="text-pink-500" />
                        Mental Wellness Tips
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {planToShow.mental_wellness_tips.map((item, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-start gap-2 p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg"
                          >
                            <Brain className="size-4 text-pink-500 shrink-0 mt-0.5" />
                            <p className="text-sm">{item}</p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Medicines Disclaimer */}
                  <Card className="border-amber-500/30 bg-amber-500/5">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="text-amber-500" />
                        Medication Disclaimer
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-amber-900 dark:text-amber-100">
                        {planToShow.medicines_disclaimer || "This plan is for educational purposes only. Always follow your healthcare provider's specific medication instructions. Never start, stop, or change medications without professional guidance."}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </ScrollArea>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <Activity className="size-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-xl font-semibold mb-2">No Recovery Plan Generated</h3>
              <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                Click &ldquo;Generate Recovery Plan&rdquo; to create a personalized plan based on your latest prediction.
              </p>
              <Button onClick={handleGenerate} size="lg" disabled={isGenerating}>
                {isGenerating ? (
                  <>
                    <RefreshCw className="mr-2 size-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 size-4" />
                    Generate Recovery Plan
                  </>
                )}
              </Button>
              {error && (
                <Alert variant="destructive" className="mt-4 max-w-md mx-auto">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* Footer Disclaimer */}
        <Alert variant="default" className="mt-8 border-amber-500/30 bg-amber-500/5">
          <AlertTriangle className="size-4 text-amber-500" />
          <AlertTitle className="text-amber-700 dark:text-amber-400">Important Medical Disclaimer</AlertTitle>
          <AlertDescription>
            This recovery plan is generated by AI for educational purposes only and is based on your symptom assessment results.
            It is NOT a medical diagnosis, prescription, or treatment plan. The information provided should not replace professional
            medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for any health concerns,
            before starting any new treatment, or if your symptoms worsen. In case of a medical emergency, call emergency services
            immediately or go to the nearest emergency department.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}