"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { Pill, Clock, Check, X, Edit2, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ReminderStatusBadge } from "./reminder-status-badge";
import { logReminderStatus, deleteReminder } from "@/lib/api/reminders";
import { useReminderStore } from "@/lib/stores/reminder-store";
import type { Reminder } from "@/lib/api/reminders";
import { toast } from "sonner";

interface ReminderCardProps {
  reminder: Reminder;
  onEdit: (reminder: Reminder) => void;
}

export function ReminderCard({ reminder, onEdit }: ReminderCardProps) {
  const { getToken } = useAuth();
  const { removeReminder } = useReminderStore();
  const [logging, setLogging] = useState<string | null>(null);

  const handleLog = async (status: "taken" | "missed") => {
    setLogging(status);
    try {
      const token = await getToken();
      await logReminderStatus(reminder.id, status, undefined, token ?? undefined);
      toast.success(
        status === "taken" ? "Logged as taken" : "Logged as missed"
      );
    } catch {
      toast.error("Failed to log status");
    } finally {
      setLogging(null);
    }
  };

  const handleDelete = async () => {
    try {
      const token = await getToken();
      await deleteReminder(reminder.id, token ?? undefined);
      removeReminder(reminder.id);
      toast.success("Reminder deleted");
    } catch {
      toast.error("Failed to delete reminder");
    }
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
            <Pill className="size-5 text-primary" />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold">{reminder.medicine_name}</h3>
              <ReminderStatusBadge status={reminder.status} />
            </div>

          <p className="mt-1 text-sm text-muted-foreground">
            {reminder.dosage} | {reminder.frequency.replace(/_/g, " ")}
          </p>

          <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="size-3" />
              {reminder.start_time}
            </span>
            <span>{reminder.duration_days} days</span>
            {reminder.email_reminder && <span>Email reminders</span>}
            {reminder.frequency === "specific_days" && reminder.schedule_details?.days && (
              <span>Days: {reminder.schedule_details.days.join(", ")}</span>
            )}
          </div>

            {reminder.next_due_at && (
              <p className="mt-1 text-xs text-muted-foreground">
                Next due: {new Date(reminder.next_due_at).toLocaleString()}
              </p>
            )}
          </div>

          <div className="flex shrink-0 items-center gap-1">
            {reminder.status === "active" && (
              <>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-8 w-8 p-0"
                  onClick={() => handleLog("taken")}
                  disabled={logging !== null}
                  aria-label="Mark as taken"
                >
                  <Check className="size-4 text-success" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-8 w-8 p-0"
                  onClick={() => handleLog("missed")}
                  disabled={logging !== null}
                  aria-label="Mark as missed"
                >
                  <X className="size-4 text-destructive" />
                </Button>
              </>
            )}
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              onClick={() => onEdit(reminder)}
              aria-label="Edit reminder"
            >
              <Edit2 className="size-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0 text-destructive"
              onClick={handleDelete}
              aria-label="Delete reminder"
            >
              <Trash2 className="size-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
