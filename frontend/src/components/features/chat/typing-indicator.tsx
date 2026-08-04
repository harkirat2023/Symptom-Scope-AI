"use client";

import { Loader2, Bot } from "lucide-react";
import { cn } from "@/lib/utils";

export function TypingIndicator() {
  return (
    <div className={cn("flex items-center gap-2 py-2")}>
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <Bot className="size-4 text-primary" />
      </div>
      <div className="flex max-w-[80%] items-end gap-1 rounded-2xl bg-muted px-4 py-2.5">
        <div className="flex gap-1" aria-label="Assistant is typing">
          <Loader2 className="size-4 text-muted-foreground animate-pulse" style={{ animationDelay: "0ms" }} />
          <Loader2 className="size-4 text-muted-foreground animate-pulse" style={{ animationDelay: "150ms" }} />
          <Loader2 className="size-4 text-muted-foreground animate-pulse" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}