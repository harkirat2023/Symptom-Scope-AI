"use client";

import { ChevronLeft, Activity } from "lucide-react";
import type { UseFormRegister, FieldErrors, Control } from "react-hook-form";
import { useController } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { SymptomFormValues } from "@/lib/validations/symptom-form";

const DURATION_OPTIONS = [
  "Just started (less than a day)",
  "A few days (1-3 days)",
  "About a week (4-7 days)",
  "More than a week (1-2 weeks)",
  "Several weeks (2+ weeks)",
  "Chronic (months)",
];

interface DetailsStepProps {
  register: UseFormRegister<SymptomFormValues>;
  errors: FieldErrors<SymptomFormValues>;
  control: Control<SymptomFormValues>;
  onBack: () => void;
  onStartAnalysis: () => void;
}

export function DetailsStep({
  register,
  errors,
  control,
  onBack,
  onStartAnalysis,
}: DetailsStepProps) {
  const { field: painField } = useController({
    name: "painLevel",
    control,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Additional Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="details-age">Age</Label>
            <Input
              id="details-age"
              type="number"
              placeholder="Your age"
              {...register("age", { setValueAs: (v) => (v === "" ? null : Number(v)) })}
            />
            {errors.age && (
              <p className="text-sm text-destructive">{errors.age.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="details-gender">Gender</Label>
            <select
              id="details-gender"
              {...register("gender")}
              className="flex h-8 w-full min-w-0 rounded-lg border border-input bg-transparent px-2.5 py-1 text-base transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:text-sm"
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="details-duration">How long have you had these symptoms?</Label>
          <select
            id="details-duration"
            {...register("symptomDuration")}
            className="flex h-8 w-full min-w-0 rounded-lg border border-input bg-transparent px-2.5 py-1 text-base transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:text-sm"
          >
            <option value="">Select duration</option>
            {DURATION_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label>
            Pain Level: {painField.value ?? "Not specified"}
          </Label>
          <input
            type="range"
            min="0"
            max="10"
            {...painField}
            value={painField.value ?? 0}
            onChange={(e) => painField.onChange(parseInt(e.target.value))}
            className="w-full accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>No pain</span>
            <span>Mild</span>
            <span>Moderate</span>
            <span>Severe</span>
            <span>Worst pain</span>
          </div>
        </div>

        <div className="flex justify-between pt-4 border-t">
          <Button variant="outline" onClick={onBack}>
            <ChevronLeft className="mr-1 size-4" />
            Back
          </Button>
          <Button onClick={onStartAnalysis}>
            Start Analysis
            <Activity className="ml-1 size-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
