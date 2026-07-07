"use client";

import { motion } from "framer-motion";
import { Lightbulb } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface HealthInsightsProps {
  insights: string[];
}

export function HealthInsights({ insights }: HealthInsightsProps) {
  if (insights.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Lightbulb className="size-4 text-warning" />
            Actionable Health Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="max-h-64">
            <ul className="space-y-2">
              {insights.map((insight, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span
                    className={cn(
                      "mt-1.5 size-2 rounded-full shrink-0",
                      insight.includes("severe") || insight.includes("below 60%")
                        ? "bg-destructive"
                        : insight.includes("Rising") || insight.includes("recurring")
                        ? "bg-warning"
                        : "bg-primary"
                    )}
                  />
                  {insight}
                </li>
              ))}
            </ul>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}
