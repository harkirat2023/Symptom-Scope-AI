"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRiskScoreStore } from "@/lib/stores/risk-score-store";
import type { UserHealthProfile } from "@/lib/api/risk-score";

const DIET_OPTIONS: { value: UserHealthProfile["diet_type"]; label: string }[] = [
  { value: "balanced", label: "Balanced" },
  { value: "unhealthy", label: "Unhealthy" },
  { value: "irregular", label: "Irregular" },
];

const SMOKING_OPTIONS: {
  value: UserHealthProfile["smoking_status"];
  label: string;
}[] = [
  { value: "never", label: "Never" },
  { value: "former", label: "Former" },
  { value: "current", label: "Current" },
];

const COMMON_CONDITIONS = [
  "Diabetes",
  "Hypertension",
  "Asthma",
  "Heart Disease",
  "Thyroid Disorder",
  "Arthritis",
];

function FormInner({
  profile,
  onSaved,
}: {
  profile: ReturnType<typeof useRiskScoreStore.getState>["profile"];
  onSaved: () => void;
}) {
  const { updateProfile, loading, error } = useRiskScoreStore();

  const [bmi, setBmi] = useState(profile?.bmi?.toString() ?? "");
  const [exerciseFrequency, setExerciseFrequency] = useState(
    profile?.exercise_frequency?.toString() ?? ""
  );
  const [dietType, setDietType] = useState(profile?.diet_type ?? "");
  const [smokingStatus, setSmokingStatus] = useState(
    profile?.smoking_status ?? ""
  );
  const [sleepHours, setSleepHours] = useState(
    profile?.sleep_hours?.toString() ?? ""
  );
  const [selectedConditions, setSelectedConditions] = useState<string[]>(
    profile?.existing_conditions ?? []
  );
  const [saved, setSaved] = useState(false);

  const toggleCondition = (condition: string) => {
    setSelectedConditions((prev) =>
      prev.includes(condition)
        ? prev.filter((c) => c !== condition)
        : [...prev, condition]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(false);

    const data: UserHealthProfile = {};
    if (bmi) data.bmi = parseFloat(bmi);
    if (exerciseFrequency)
      data.exercise_frequency = parseInt(exerciseFrequency, 10);
    if (dietType) data.diet_type = dietType as UserHealthProfile["diet_type"];
    if (smokingStatus)
      data.smoking_status =
        smokingStatus as UserHealthProfile["smoking_status"];
    if (sleepHours) data.sleep_hours = parseFloat(sleepHours);
    if (selectedConditions.length > 0)
      data.existing_conditions = selectedConditions;

    await updateProfile(data);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
    onSaved();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium">BMI</label>
          <input
            type="number"
            step="0.1"
            placeholder="e.g. 24.5"
            value={bmi}
            onChange={(e) => setBmi(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Exercise (days/week)
          </label>
          <input
            type="number"
            min={0}
            max={7}
            placeholder="e.g. 3"
            value={exerciseFrequency}
            onChange={(e) => setExerciseFrequency(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Diet Type</label>
          <select
            value={dietType}
            onChange={(e) => setDietType(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm"
          >
            <option value="">Select...</option>
            {DIET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Smoking Status
          </label>
          <select
            value={smokingStatus}
            onChange={(e) => setSmokingStatus(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm"
          >
            <option value="">Select...</option>
            {SMOKING_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Sleep (hours/night)
          </label>
          <input
            type="number"
            step="0.5"
            min={1}
            max={24}
            placeholder="e.g. 7"
            value={sleepHours}
            onChange={(e) => setSleepHours(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium">
          Existing Conditions
        </label>
        <div className="flex flex-wrap gap-2">
          {COMMON_CONDITIONS.map((condition) => (
            <button
              key={condition}
              type="button"
              onClick={() => toggleCondition(condition)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                selectedConditions.includes(condition)
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
              }`}
            >
              {condition}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "Saving..." : "Save Profile"}
        </button>
        {saved && (
          <span className="text-xs text-green-600">
            Profile saved successfully
          </span>
        )}
        {error && (
          <span className="text-xs text-red-600">{error}</span>
        )}
      </div>
    </form>
  );
}

export default function HealthProfileForm() {
  const { getToken } = useAuth();
  const { profile, fetchProfile, setGetToken } = useRiskScoreStore();

  useEffect(() => {
    setGetToken(getToken);
  }, [setGetToken, getToken]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return (
    <FormInner
      key={profile?.updated_at ?? "loading"}
      profile={profile}
      onSaved={() => fetchProfile()}
    />
  );
}
