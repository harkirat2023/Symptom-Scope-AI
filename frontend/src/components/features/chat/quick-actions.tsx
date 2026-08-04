"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const QUICK_ACTIONS = [
  { label: "Explain my disease", prompt: "Explain my predicted disease in simple terms" },
  { label: "Recovery timeline", prompt: "What is my expected recovery timeline?" },
  { label: "Diet plan", prompt: "What should I eat and avoid during recovery?" },
  { label: "Foods to avoid", prompt: "What foods should I avoid with my condition?" },
  { label: "Exercise", prompt: "What exercises are safe during my recovery?" },
  { label: "Precautions", prompt: "What precautions should I take?" },
  { label: "When to see a doctor", prompt: "When should I visit a doctor?" },
  { label: "Emergency symptoms", prompt: "What emergency symptoms should I watch for?" },
  { label: "Daily routine", prompt: "What should my daily recovery routine look like?" },
] as const;

interface QuickActionsProps {
  onActionClick: (prompt: string) => void;
  disabled?: boolean;
  className?: string;
}

export function QuickActions({ onActionClick, disabled, className }: QuickActionsProps) {
  return (
    <div
      className={cn("flex flex-wrap gap-2", className)}
      role="list"
      aria-label="Quick action prompts"
    >
      {QUICK_ACTIONS.map((action) => (
        <Button
          key={action.label}
          type="button"
          variant="outline"
          size="sm"
          onClick={() => onActionClick(action.prompt)}
          disabled={disabled}
          className={cn(
            "h-8 px-3 text-xs font-medium transition-all hover:bg-accent hover:text-accent-foreground",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          role="listitem"
        >
          {action.label}
        </Button>
      ))}
    </div>
  );
}