import { ChevronUp, ChevronDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

export function TrendIcon({ direction, className }: { direction: string; className?: string }) {
  if (direction === "increasing") return <ChevronUp className={cn("size-4 text-destructive", className)} />;
  if (direction === "decreasing") return <ChevronDown className={cn("size-4 text-success", className)} />;
  return <Minus className={cn("size-4 text-muted-foreground", className)} />;
}
