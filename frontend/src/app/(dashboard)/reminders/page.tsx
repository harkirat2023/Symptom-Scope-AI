"use client";

import { motion } from "framer-motion";
import { ReminderList } from "@/components/features/reminders/reminder-list";

export default function RemindersPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-bold">Medicine Reminders</h1>
        <p className="text-muted-foreground">
          Manage your medication reminders and track adherence
        </p>
      </div>

      <ReminderList />
    </motion.div>
  );
}
