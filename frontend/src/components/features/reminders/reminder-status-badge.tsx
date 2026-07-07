"use client";

import { cn } from "@/lib/utils";
import type { ReminderStatus } from "@/lib/api/reminders";

const statusConfig: Record<ReminderStatus, { label: string; className: string }> = {
  active: {
    label: "Active",
    className: "bg-success/10 text-success border-success/20",
  },
  paused: {
    label: "Paused",
    className: "bg-warning/10 text-warning border-warning/20",
  },
  completed: {
    label: "Completed",
    className: "bg-muted text-muted-foreground border-border/40",
  },
};

interface ReminderStatusBadgeProps {
  status: ReminderStatus;
}

export function ReminderStatusBadge({ status }: ReminderStatusBadgeProps) {
  const config = statusConfig[status];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className
      )}
    >
      {config.label}
    </span>
  );
}
