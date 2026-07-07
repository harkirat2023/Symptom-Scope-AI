"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Pill, Clock, ChevronRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { fetchUpcomingReminder } from "@/lib/api/reminders";

export function ReminderDashboardCard() {
  const { getToken } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ["upcoming-reminder"],
    queryFn: async () => {
      const token = await getToken();
      return fetchUpcomingReminder(token ?? undefined);
    },
    staleTime: 60_000,
  });

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-4">
          <Skeleton className="h-5 w-32 mb-2" />
          <Skeleton className="h-4 w-48" />
        </CardContent>
      </Card>
    );
  }

  if (!data?.has_upcoming || !data.reminder) {
    return null;
  }

  const reminder = data.reminder;

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <Pill className="size-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium">Next Reminder</p>
              <p className="text-lg font-bold">{reminder.medicine_name}</p>
              <p className="text-sm text-muted-foreground">
                {reminder.dosage}
              </p>
              <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="size-3" />
                {reminder.start_time}
              </div>
            </div>
          </div>
          <Link href="/reminders">
            <Button variant="ghost" size="sm" className="gap-1">
              View All
              <ChevronRight className="size-3" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
