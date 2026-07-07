import { create } from "zustand";
import type { Reminder, ReminderStatus } from "@/lib/api/reminders";

interface ReminderState {
  reminders: Reminder[];
  filter: ReminderStatus | "all";
  isLoading: boolean;
  error: string | null;

  setReminders: (reminders: Reminder[]) => void;
  addReminder: (reminder: Reminder) => void;
  updateReminder: (id: string, data: Partial<Reminder>) => void;
  removeReminder: (id: string) => void;
  setFilter: (filter: ReminderStatus | "all") => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useReminderStore = create<ReminderState>((set) => ({
  reminders: [],
  filter: "all",
  isLoading: false,
  error: null,

  setReminders: (reminders) => set({ reminders }),
  addReminder: (reminder) =>
    set((s) => ({ reminders: [reminder, ...s.reminders] })),
  updateReminder: (id, data) =>
    set((s) => ({
      reminders: s.reminders.map((r) =>
        r.id === id ? { ...r, ...data } : r
      ),
    })),
  removeReminder: (id) =>
    set((s) => ({
      reminders: s.reminders.filter((r) => r.id !== id),
    })),
  setFilter: (filter) => set({ filter }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
