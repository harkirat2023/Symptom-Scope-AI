"use client";

import { cn } from "@/lib/utils";

export type CheckerStep = "symptoms" | "details" | "analyzing" | "results";

const STEPS: { key: CheckerStep; label: string }[] = [
  { key: "symptoms", label: "Symptoms" },
  { key: "details", label: "Details" },
  { key: "analyzing", label: "Analysis" },
  { key: "results", label: "Results" },
];

export function StepIndicator({ current }: { current: CheckerStep }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current);

  return (
    <div className="flex items-center justify-center gap-2 mb-8">
      {STEPS.map((step, idx) => {
        const isActive = idx <= currentIndex;
        const isCurrent = step.key === current;
        return (
          <div key={step.key} className="flex items-center gap-2">
            <div
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground",
                isCurrent && "ring-2 ring-primary ring-offset-2"
              )}
            >
              {idx + 1}
            </div>
            <span
              className={cn(
                "text-sm hidden sm:inline",
                isActive ? "text-foreground font-medium" : "text-muted-foreground"
              )}
            >
              {step.label}
            </span>
            {idx < STEPS.length - 1 && (
              <div
                className={cn(
                  "w-8 h-0.5 sm:w-12",
                  idx < currentIndex ? "bg-primary" : "bg-muted"
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
