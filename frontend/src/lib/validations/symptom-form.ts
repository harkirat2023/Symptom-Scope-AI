import { z } from "zod";

export const symptomFormSchema = z.object({
  symptoms: z
    .array(z.string())
    .min(1, "Select at least one symptom"),
  age: z
    .number()
    .int("Age must be a whole number")
    .min(1, "Age must be at least 1")
    .max(150, "Age must be at most 150")
    .nullable()
    .default(null),
  gender: z
    .enum(["male", "female", "other"])
    .nullable()
    .default(null),
  existingConditions: z
    .array(z.string())
    .default([]),
  symptomDuration: z
    .string()
    .default(""),
  painLevel: z
    .number()
    .int("Pain level must be a whole number")
    .min(0, "Pain level must be 0 or more")
    .max(10, "Pain level must be 10 or less")
    .nullable()
    .default(null),
});

export type SymptomFormValues = z.input<typeof symptomFormSchema>;

