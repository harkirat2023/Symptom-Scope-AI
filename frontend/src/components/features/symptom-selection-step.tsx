"use client";

import { useState, useMemo } from "react";
import { useController, type Control } from "react-hook-form";
import { X, Search, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import type { SymptomFormValues } from "@/lib/validations/symptom-form";

const AVAILABLE_SYMPTOMS = [
  "Fever", "Dry Cough", "Fatigue", "Headache", "Sore Throat",
  "Body Ache", "Chest Pain", "Shortness of Breath", "Nausea",
  "Vomiting", "Diarrhea", "Loss of Taste", "Loss of Smell",
  "Runny Nose", "Sneezing", "Joint Pain", "Chills", "Sweating",
  "Dizziness", "Abdominal Pain", "Rash", "Muscle Weakness",
  "Blurred Vision", "Confusion", "Seizure",
  "Arm Pain", "Jaw Pain", "Facial Drooping", "Speech Difficulty",
  "Sensitivity to Light", "Sensitivity to Sound",
];

interface SymptomSelectionStepProps {
  control: Control<SymptomFormValues>;
  onComplete: () => void;
}

export function SymptomSelectionStep({
  control,
  onComplete,
}: SymptomSelectionStepProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const { field, fieldState } = useController({
    name: "symptoms",
    control,
  });

  const selectedSymptoms = field.value;
  const error = fieldState.error?.message;

  const filteredSymptoms = useMemo(
    () =>
      AVAILABLE_SYMPTOMS.filter(
        (s) =>
          s.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !selectedSymptoms.includes(s)
      ),
    [searchQuery, selectedSymptoms]
  );

  const toggleSymptom = (symptom: string) => {
    const updated = selectedSymptoms.includes(symptom)
      ? selectedSymptoms.filter((s) => s !== symptom)
      : [...selectedSymptoms, symptom];
    field.onChange(updated);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>What symptoms are you experiencing?</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search symptoms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {selectedSymptoms.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedSymptoms.map((symptom) => (
              <Badge
                key={symptom}
                variant="default"
                className="cursor-pointer gap-1 pr-1"
                onClick={() => toggleSymptom(symptom)}
              >
                {symptom}
                <X className="size-3" />
              </Badge>
            ))}
          </div>
        )}

        <div className="max-h-60 overflow-y-auto space-y-1">
          {filteredSymptoms.map((symptom) => (
            <button
              key={symptom}
              type="button"
              onClick={() => toggleSymptom(symptom)}
              className="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-muted transition-colors"
            >
              {symptom}
            </button>
          ))}
          {filteredSymptoms.length === 0 && searchQuery && (
            <p className="text-sm text-muted-foreground px-3 py-2">
              No symptoms found. Try a different search term.
            </p>
          )}
        </div>

        <div className="flex justify-between items-center pt-4 border-t">
          <p className="text-sm text-muted-foreground">
            {selectedSymptoms.length} symptom{selectedSymptoms.length !== 1 ? "s" : ""} selected
          </p>
          <div className="flex items-center gap-3">
            {error && (
              <p className="text-sm text-destructive" role="alert">{error}</p>
            )}
            <Button
              onClick={onComplete}
              disabled={selectedSymptoms.length === 0}
            >
              Next
              <ChevronRight className="ml-1 size-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
