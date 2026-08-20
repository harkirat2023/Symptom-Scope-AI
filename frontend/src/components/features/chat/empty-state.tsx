"use client";

import { MessageCircle, Bot, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const EXAMPLE_PROMPTS = [
  { label: "Create my recovery plan", prompt: "Please generate my personalized recovery plan" },
  { label: "Set up medication reminders", prompt: "Set up a reminder for my medication in the morning" },
  { label: "Save my email for alerts", prompt: "Save my email so I can get reminder notifications" },
  { label: "What should I eat?", prompt: "What should I eat and avoid during recovery?" },
] as const;

interface EmptyStateProps {
  onPromptClick: (prompt: string) => void;
  className?: string;
}

export function EmptyState({ onPromptClick, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center h-full px-6 text-center",
        className
      )}
      role="region"
      aria-label="Chat empty state"
    >
      <div className="mx-auto mb-6 flex size-16 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <Bot className="size-8 text-primary" />
      </div>
      <h3 className="mb-2 text-lg font-semibold text-foreground">Health Assistant</h3>
      <p className="mb-6 max-w-sm text-sm text-muted-foreground">
        I can guide your recovery, set up medication reminders, save your email
        for alerts, and answer questions about your condition.
      </p>
      <div className="w-full max-w-sm space-y-2" role="list" aria-label="Example prompts">
        {EXAMPLE_PROMPTS.map((item) => (
          <Button
            key={item.label}
            type="button"
            variant="outline"
            className={cn(
              "w-full justify-start gap-3 px-4 py-2.5 text-sm font-medium",
              "hover:bg-accent hover:text-accent-foreground",
              "transition-colors"
            )}
            onClick={() => onPromptClick(item.prompt)}
            role="listitem"
          >
            <MessageCircle className="size-4 shrink-0 text-muted-foreground" />
            <span className="truncate">{item.label}</span>
            <ArrowRight className="size-4 shrink-0 text-muted-foreground" />
          </Button>
        ))}
      </div>
      <p className="mt-6 text-xs text-muted-foreground/60">
        Educational purposes only. Not a substitute for professional medical advice.
      </p>
    </div>
  );
}