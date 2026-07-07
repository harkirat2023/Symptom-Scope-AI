"use client";

import { Activity } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function AnalyzingStep() {
  return (
    <Card>
      <CardContent className="py-16 text-center">
        <div className="mx-auto mb-6 flex size-16 items-center justify-center rounded-full bg-primary/10">
          <Activity className="size-8 animate-pulse text-primary" />
        </div>
        <h3 className="text-xl font-semibold mb-2">
          Analyzing Your Symptoms
        </h3>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          Our AI is processing your symptoms against our medical knowledge base.
          This will only take a moment.
        </p>
        <div className="space-y-3 max-w-sm mx-auto">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-5/6" />
        </div>
      </CardContent>
    </Card>
  );
}
