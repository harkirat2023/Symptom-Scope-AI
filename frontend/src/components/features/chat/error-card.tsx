"use client";

import { AlertCircle, RefreshCw, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { cn } from "@/lib/utils";

interface ErrorCardProps {
  message: string;
  onRetry: () => void;
  onDismiss: () => void;
  className?: string;
}

export function ErrorCard({ message, onRetry, onDismiss, className }: ErrorCardProps) {
  return (
    <Alert
      variant="destructive"
      className={cn("mb-4 border-destructive/30 bg-destructive/10", className)}
      role="alert"
    >
      <AlertCircle className="size-4 text-destructive" />
      <div className="flex-1 min-w-0">
        <AlertTitle className="text-sm font-medium">Connection error</AlertTitle>
        <AlertDescription className="text-sm">
          {message}
        </AlertDescription>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="gap-1.5"
          disabled={false}
        >
          <RefreshCw className="size-3.5" />
          Retry
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={onDismiss}
          className="size-7 text-destructive/80 hover:bg-destructive/10"
          aria-label="Dismiss error"
        >
          <X className="size-3.5" />
        </Button>
      </div>
    </Alert>
  );
}