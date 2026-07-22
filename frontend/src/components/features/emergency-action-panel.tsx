"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import {
  AmbulanceIcon,
  HospitalIcon,
  PhoneIcon,
  StarIcon,
  MapPinIcon,
  VideoIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchHospitals, type HospitalResponse } from "@/lib/api/predictions";

interface EmergencyActionPanelProps {
  predictedDisease?: string;
}

function HospitalCard({ hospital }: { hospital: HospitalResponse }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border p-3 text-sm">
      <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <HospitalIcon className="size-5 text-primary" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{hospital.name}</p>
        <p className="mt-0.5 flex items-center gap-1 text-muted-foreground">
          <MapPinIcon className="size-3" />
          {hospital.location}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="flex items-center gap-1 text-amber-500">
            <StarIcon className="size-3" />
            {hospital.rating.toFixed(1)}
          </span>
          <span className="text-muted-foreground">
            {hospital.distance_km?.toFixed(1)} km
          </span>
          {hospital.emergency && (
            <Badge variant="outline" className="text-destructive border-destructive/40 text-[10px] px-1.5 py-0">
              24/7 Emergency
            </Badge>
          )}
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          {hospital.phone}
        </p>
      </div>
    </div>
  );
}

export function EmergencyActionPanel({ predictedDisease }: EmergencyActionPanelProps) {
  const { getToken } = useAuth();
  const [hospitalsOpen, setHospitalsOpen] = useState(false);
  const [teleconsultOpen, setTeleconsultOpen] = useState(false);

  const {
    data: hospitalsData,
    isLoading: hospitalsLoading,
  } = useQuery({
    queryKey: ["emergency-hospitals"],
    queryFn: async () => {
      const token = await getToken();
      return fetchHospitals({ emergency_only: true, sort_by: "rating", limit: 5 }, token ?? undefined);
    },
    enabled: hospitalsOpen,
    staleTime: 60_000,
  });

  return (
    <div
      className="mt-4 space-y-3"
      role="group"
      aria-label="Emergency action options"
    >
      <p className="text-sm font-semibold text-destructive">
        Recommended Actions
      </p>

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        <Button
          variant="destructive"
          size="lg"
          className="w-full gap-2 sm:w-auto"
          onClick={() => window.location.assign("tel:911")}
          aria-label="Call ambulance immediately"
        >
          <AmbulanceIcon className="size-5" />
          Call Ambulance
        </Button>

        <Button
          variant="outline"
          size="lg"
          className="w-full gap-2 border-destructive/30 text-destructive hover:bg-destructive/10 sm:w-auto"
          onClick={() => setHospitalsOpen(true)}
          aria-label="Find nearby hospitals with emergency services"
        >
          <HospitalIcon className="size-5" />
          Nearby Hospitals
        </Button>

        <Button
          variant="outline"
          size="lg"
          className="w-full gap-2 sm:w-auto"
          onClick={() => setTeleconsultOpen(true)}
          aria-label="Start teleconsultation with a doctor"
        >
          <VideoIcon className="size-5" />
          Teleconsultation
        </Button>
      </div>

      <Dialog open={hospitalsOpen} onOpenChange={setHospitalsOpen}>
        <DialogContent className="sm:max-w-lg" aria-label="Nearby hospitals">
          <DialogHeader>
            <DialogTitle>Nearby Hospitals with Emergency Services</DialogTitle>
            <DialogDescription>
              Hospitals that can provide immediate emergency care.
            </DialogDescription>
          </DialogHeader>
          <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
            {hospitalsLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-start gap-3 rounded-lg border p-3">
                  <Skeleton className="size-10 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))
            ) : hospitalsData && hospitalsData.hospitals.length > 0 ? (
              hospitalsData.hospitals.map((hospital) => (
                <HospitalCard key={hospital.name} hospital={hospital} />
              ))
            ) : (
              <p className="py-4 text-center text-sm text-muted-foreground">
                No emergency hospitals found in your area. Please call emergency services.
              </p>
            )}
          </div>
          <div className="mt-2 flex justify-end">
            <Button
              variant="destructive"
              size="sm"
              className="gap-2"
              onClick={() => window.location.assign("tel:911")}
              aria-label="Call ambulance"
            >
              <PhoneIcon className="size-4" />
              Call Ambulance Now
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={teleconsultOpen} onOpenChange={setTeleconsultOpen}>
        <DialogContent className="sm:max-w-md" aria-label="Teleconsultation options">
          <DialogHeader>
            <DialogTitle>Teleconsultation</DialogTitle>
            <DialogDescription>
              Speak with a healthcare professional remotely.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
              <p className="flex items-center gap-2 text-sm font-medium text-blue-800 dark:text-blue-200">
                <VideoIcon className="size-4" />
                Telemedicine Consultation
              </p>
              <p className="mt-1 text-xs text-blue-700 dark:text-blue-300">
                Connect with a licensed doctor via video call for immediate
                guidance on your symptoms{predictedDisease ? ` related to ${predictedDisease}` : ""}.
              </p>
            </div>
            <div className="space-y-2 text-sm">
              <p className="font-medium">Available options:</p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
                  <span>
                    <strong>Practo</strong> — Instant video consultations with
                    specialists
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
                  <span>
                    <strong>Apollo 24/7</strong> — Online doctor consultations
                    and medicine delivery
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
                  <span>
                    <strong>1mg</strong> — Consult doctors online and get
                    prescriptions
                  </span>
                </li>
              </ul>
            </div>
            <div className="rounded-lg border p-3 text-xs text-muted-foreground">
              <p className="font-medium text-foreground">Note:</p>
              Teleconsultation is not a substitute for emergency care.
              If you are experiencing a life-threatening emergency, call emergency services immediately.
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
