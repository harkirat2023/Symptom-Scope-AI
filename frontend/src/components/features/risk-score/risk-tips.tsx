"use client";

import { Lightbulb } from "lucide-react";

export default function RiskTips({ tips }: { tips: string[] }) {
  if (tips.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border p-4">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
        <Lightbulb className="h-4 w-4 text-yellow-500" />
        Recommendations
      </h3>
      <ul className="space-y-2">
        {tips.map((tip, i) => (
          <li
            key={i}
            className="flex gap-2 text-sm text-muted-foreground"
          >
            <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
            {tip}
          </li>
        ))}
      </ul>
    </div>
  );
}
