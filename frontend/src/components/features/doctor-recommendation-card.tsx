"use client";

import { StarIcon, MapPinIcon, CalendarIcon, StethoscopeIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import type { DoctorResponse } from "@/lib/api/predictions";

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

interface DoctorRecommendationCardProps {
  doctor: DoctorResponse;
}

export function DoctorRecommendationCard({ doctor }: DoctorRecommendationCardProps) {
  return (
    <Card className="flex items-start gap-4 p-4">
      <Avatar className="size-12 shrink-0">
        {doctor.image_url ? (
          <AvatarImage src={doctor.image_url} alt={`${doctor.name}'s photo`} />
        ) : null}
        <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
          {getInitials(doctor.name)}
        </AvatarFallback>
      </Avatar>

      <div className="min-w-0 flex-1">
        <h3 className="text-base font-semibold leading-tight">
          {doctor.name}
        </h3>
        <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
          <StethoscopeIcon className="size-3.5 shrink-0" />
          {doctor.specialty}
        </p>

        <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <StarIcon className="size-3.5 text-amber-500" />
            {doctor.rating.toFixed(1)}
          </span>
          <span className="flex items-center gap-1">
            <MapPinIcon className="size-3.5" />
            {doctor.distance_km?.toFixed(1)} km
          </span>
          <span className="flex items-center gap-1">
            <CalendarIcon className="size-3.5" />
            {doctor.availability?.join(", ") || "Available"}
          </span>
        </div>
      </div>

      <Button
        variant="default"
        size="sm"
        className="shrink-0"
        onClick={() => window.open("https://www.practo.com/consult", "_blank", "noopener")}
        aria-label={`Book consultation with ${doctor.name}`}
      >
        Book Consultation
      </Button>
    </Card>
  );
}
