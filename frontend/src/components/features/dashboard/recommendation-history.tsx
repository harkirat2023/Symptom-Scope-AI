"use client";

import { motion } from "framer-motion";
import { Stethoscope, Lightbulb } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { PredictionRecord } from "@/lib/api/predictions";

interface RecommendationHistoryProps {
  predictions: PredictionRecord[];
}

const DISEASE_RECOMMENDATIONS: Record<string, { specialist: string; precautions: string[] }> = {
  Influenza: {
    specialist: "General Physician",
    precautions: ["Drink plenty of fluids", "Rest adequately", "Monitor temperature", "Visit physician if symptoms worsen"],
  },
  "Common Cold": {
    specialist: "General Physician",
    precautions: ["Rest and stay hydrated", "Use over-the-counter cold remedies", "Gargle with warm salt water", "Get plenty of sleep"],
  },
  Migraine: {
    specialist: "Neurologist",
    precautions: ["Rest in a dark, quiet room", "Apply cold compress to forehead", "Stay hydrated", "Avoid triggers like bright lights"],
  },
  Asthma: {
    specialist: "Pulmonologist",
    precautions: ["Use prescribed inhaler as needed", "Avoid allergens and triggers", "Sit upright to ease breathing", "Seek emergency care if severe"],
  },
  Allergy: {
    specialist: "General Physician",
    precautions: ["Take antihistamines as prescribed", "Avoid known allergens", "Keep windows closed during high pollen", "Wear a mask if necessary"],
  },
  Pneumonia: {
    specialist: "Pulmonologist",
    precautions: ["Complete prescribed antibiotic course", "Rest and stay hydrated", "Monitor oxygen levels", "Seek immediate care if breathing worsens"],
  },
  Bronchitis: {
    specialist: "Pulmonologist",
    precautions: ["Rest and drink warm fluids", "Use a humidifier", "Avoid smoke and irritants", "Take prescribed medications as directed"],
  },
  "Heart Attack": {
    specialist: "Cardiologist",
    precautions: ["Call emergency services immediately", "Chew aspirin if prescribed", "Rest and stay calm", "Do not drive yourself to hospital"],
  },
  Stroke: {
    specialist: "Neurologist",
    precautions: ["Call emergency services immediately", "Note the time symptoms started", "Keep patient calm and lying down", "Do not give food or drink"],
  },
  "Food Poisoning": {
    specialist: "Gastroenterologist",
    precautions: ["Stay hydrated with clear fluids", "Avoid solid foods until vomiting stops", "Eat bland foods when ready", "Seek care if symptoms persist"],
  },
  "Ear Infection": {
    specialist: "ENT Specialist",
    precautions: ["Apply warm compress to ear", "Take prescribed pain relievers", "Complete antibiotic course if prescribed", "Avoid getting water in ear"],
  },
};

const defaultRecommendation = {
  specialist: "General Physician",
  precautions: ["Rest adequately", "Stay hydrated", "Monitor symptoms", "Consult a healthcare professional if symptoms persist"],
};

export function RecommendationHistory({ predictions }: RecommendationHistoryProps) {
  if (predictions.length === 0) return null;

  const sortedPredictions = [...predictions].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const latestPredictions = sortedPredictions.slice(0, 10);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Stethoscope className="size-4 text-primary" />
            Recommendation History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="max-h-80">
            <div className="space-y-4">
              {latestPredictions.map((record) => {
                const rec = DISEASE_RECOMMENDATIONS[record.prediction] ?? defaultRecommendation;
                return (
                  <div key={record.id} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{record.prediction}</span>
                        <Badge
                          className={cn(
                            "text-[10px] px-1.5 py-0",
                            record.severity === "Severe" && "bg-destructive/10 text-destructive border-destructive/20",
                            record.severity === "Moderate" && "bg-warning/10 text-warning border-warning/20",
                            record.severity === "Mild" && "bg-success/10 text-success border-success/20",
                          )}
                        >
                          {record.severity}
                        </Badge>
                      </div>
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(record.timestamp).toLocaleDateString("en-US", {
                          month: "short", day: "numeric",
                        })}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 mb-2">
                      <Stethoscope className="size-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">
                        Recommended: {rec.specialist}
                      </span>
                    </div>
                    <div className="flex items-start gap-1.5">
                      <Lightbulb className="size-3 text-warning mt-0.5 shrink-0" />
                      <ul className="space-y-0.5">
                        {rec.precautions.slice(0, 3).map((precaution, i) => (
                          <li key={i} className="text-xs text-muted-foreground flex items-start gap-1">
                            <span className="mt-1 size-1 rounded-full bg-primary shrink-0" />
                            {precaution}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}
