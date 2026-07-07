"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { fetchReminders } from "@/lib/api/reminders";
import { useReminderStore } from "@/lib/stores/reminder-store";
import { ReminderCard } from "./reminder-card";
import { ReminderForm } from "./reminder-form";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, Pill } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { Reminder, ReminderStatus } from "@/lib/api/reminders";

const FILTERS: { label: string; value: ReminderStatus | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Active", value: "active" },
  { label: "Paused", value: "paused" },
  { label: "Completed", value: "completed" },
];

export function ReminderList() {
  const { getToken } = useAuth();
  const { filter, isLoading, setReminders, setLoading } = useReminderStore();
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Reminder | null>(null);

  const { error } = useQuery({
    queryKey: ["reminders", filter],
    queryFn: async () => {
      setLoading(true);
      try {
        const token = await getToken();
        const result = await fetchReminders(
          filter === "all" ? undefined : filter,
          token ?? undefined
        );
        setReminders(result.reminders);
        return result;
      } finally {
        setLoading(false);
      }
    },
  });

  const { reminders } = useReminderStore();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {FILTERS.map((f) => (
            <Button
              key={f.value}
              variant={filter === f.value ? "default" : "outline"}
              size="sm"
              onClick={() =>
                useReminderStore.getState().setFilter(f.value)
              }
            >
              {f.label}
            </Button>
          ))}
        </div>
        <Button onClick={() => { setEditing(null); setFormOpen(true); }}>
          <Pill className="mr-2 size-4" />
          New Reminder
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="size-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>Failed to load reminders.</AlertDescription>
        </Alert>
      )}

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      )}

      {!isLoading && reminders.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Pill className="size-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No reminders</h3>
            <p className="text-muted-foreground mb-4">
              Create your first medicine reminder.
            </p>
            <Button onClick={() => { setEditing(null); setFormOpen(true); }}>
              Create Reminder
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && reminders.length > 0 && (
        <div className="space-y-3">
          {reminders.map((r) => (
            <ReminderCard
              key={r.id}
              reminder={r}
              onEdit={(reminder) => {
                setEditing(reminder);
                setFormOpen(true);
              }}
            />
          ))}
        </div>
      )}

      <ReminderForm
        open={formOpen}
        onOpenChange={(open) => {
          setFormOpen(open);
          if (!open) setEditing(null);
        }}
        editReminder={editing}
      />
    </div>
  );
}
