"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { createReminder, updateReminder } from "@/lib/api/reminders";
import { useReminderStore } from "@/lib/stores/reminder-store";
import type { Reminder, ReminderFrequency } from "@/lib/api/reminders";
import { toast } from "sonner";

const formSchema = z.object({
  medicine_name: z.string().min(1, "Medicine name is required").max(100),
  dosage: z.string().min(1, "Dosage is required").max(50),
  frequency: z.enum(["daily", "specific_days"]),
  duration_days: z.coerce.number().int().min(1).max(365),
  start_time: z.string().regex(/^\d{2}:\d{2}$/, "Use HH:MM format"),
  specific_days: z.array(z.enum(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])).min(1, "Select at least one day").optional(),
  email_reminder: z.boolean().default(false),
});

type FormValues = z.infer<typeof formSchema>;

interface ReminderFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editReminder?: Reminder | null;
}

export function ReminderForm({
  open,
  onOpenChange,
  editReminder,
}: ReminderFormProps) {
  const { getToken } = useAuth();
  const { addReminder, updateReminder: updateStore } = useReminderStore();
  const [saving, setSaving] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
    watch,
    setValue,
  } = useForm<FormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(formSchema) as any,
    defaultValues: editReminder
      ? {
          medicine_name: editReminder.medicine_name,
          dosage: editReminder.dosage,
          frequency: editReminder.frequency,
          duration_days: editReminder.duration_days,
          start_time: editReminder.start_time,
          specific_days: [],
          email_reminder: editReminder.email_reminder,
        }
      : {
          medicine_name: "",
          dosage: "",
          frequency: "daily",
          duration_days: 7,
          start_time: "08:00",
          specific_days: [],
          email_reminder: false,
        },
  });

  const selectedFrequency = watch("frequency");

  const weekdays: ("Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday" | "Saturday" | "Sunday")[] = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
  ];

  const handleFrequencyChange = (value: ReminderFrequency) => {
    setValue("frequency", value);
    if (value === "specific_days") {
      setValue("specific_days", weekdays);
    } else {
      setValue("specific_days", []);
    }
  };

  const onSubmit = async (data: FormValues) => {
    setSaving(true);
    try {
      const token = await getToken();
      if (editReminder) {
        const updated = await updateReminder(
          editReminder.id,
          { ...data, status: editReminder.status },
          token ?? undefined
        );
        updateStore(editReminder.id, updated);
        toast.success("Reminder updated");
      } else {
        const created = await createReminder(data, token ?? undefined);
        addReminder(created);
        toast.success("Reminder created");
      }
      onOpenChange(false);
      reset();
    } catch {
      toast.error("Failed to save reminder");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {editReminder ? "Edit Reminder" : "New Medicine Reminder"}
          </DialogTitle>
          <DialogDescription>
            Set up a reminder for your medication.
          </DialogDescription>
        </DialogHeader>

        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        <form onSubmit={handleSubmit(onSubmit as any)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="medicine_name">Medicine Name</Label>
            <Input
              id="medicine_name"
              placeholder="e.g., Amoxicillin"
              {...register("medicine_name")}
            />
            {errors.medicine_name && (
              <p className="text-xs text-destructive">
                {errors.medicine_name.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="dosage">Dosage</Label>
            <Input
              id="dosage"
              placeholder="e.g., 500mg"
              {...register("dosage")}
            />
            {errors.dosage && (
              <p className="text-xs text-destructive">
                {errors.dosage.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="frequency">Frequency</Label>
            <Controller
              name="frequency"
              control={control}
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={(v) => {
                    if (v) field.onChange(v as ReminderFrequency);
                    handleFrequencyChange(v as ReminderFrequency);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="specific_days">Specific Days</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          {selectedFrequency === "specific_days" && (
            <div className="space-y-2">
              <Label>Days of Week</Label>
              <div className="grid grid-cols-2 gap-2">
                {weekdays.map((day) => (
                  <Controller
                    key={day}
                    name="specific_days"
                    control={control}
                    render={({ field }) => {
                      const isSelected = field.value?.includes(day) || false;
                      return (
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`day-${day}`}
                            checked={isSelected}
                            onChange={(e) => {
                              const updated = e.target.checked
                                ? [...(field.value || []), day]
                                : (field.value || []).filter((d) => d !== day);
                              field.onChange(updated);
                            }}
                            className="rounded border-gray-300"
                          />
                          <label htmlFor={`day-${day}`} className="text-sm">
                            {day}
                          </label>
                        </div>
                      );
                    }}
                  />
                ))}
              </div>
              {errors.specific_days && (
                <p className="text-xs text-destructive">
                  {errors.specific_days.message}
                </p>
              )}
            </div>
          )}

          <div className="flex gap-4">
            <div className="flex-1 space-y-2">
              <Label htmlFor="duration_days">Duration (days)</Label>
              <Input
                id="duration_days"
                type="number"
                min={1}
                max={365}
                {...register("duration_days")}
              />
            </div>
            <div className="flex-1 space-y-2">
              <Label htmlFor="start_time">Start Time</Label>
              <Input
                id="start_time"
                type="time"
                {...register("start_time")}
              />
            </div>
          </div>

          <div className="flex items-center justify-between rounded-lg border p-3">
            <div>
              <Label htmlFor="email_reminder" className="font-medium">
                Email Reminder
              </Label>
              <p className="text-xs text-muted-foreground">
                Get email notifications
              </p>
            </div>
            <Controller
              name="email_reminder"
              control={control}
              render={({ field }) => (
                <Switch
                  id="email_reminder"
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              )}
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editReminder ? "Update" : "Create Reminder"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
