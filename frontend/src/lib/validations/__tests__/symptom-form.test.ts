import { describe, it, expect } from "vitest";
import { symptomFormSchema } from "@/lib/validations/symptom-form";

describe("symptomFormSchema", () => {
  it("accepts valid input with all fields", () => {
    const result = symptomFormSchema.safeParse({
      symptoms: ["Fever", "Cough"],
      age: 30,
      gender: "male",
      existingConditions: ["Diabetes"],
      symptomDuration: "A few days",
      painLevel: 5,
    });
    expect(result.success).toBe(true);
  });

  it("accepts minimum valid input (only symptoms)", () => {
    const result = symptomFormSchema.safeParse({
      symptoms: ["Headache"],
    });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.symptoms).toEqual(["Headache"]);
      expect(result.data.age).toBeNull();
      expect(result.data.gender).toBeNull();
      expect(result.data.existingConditions).toEqual([]);
      expect(result.data.symptomDuration).toBe("");
      expect(result.data.painLevel).toBeNull();
    }
  });

  it("rejects empty symptoms array", () => {
    const result = symptomFormSchema.safeParse({
      symptoms: [],
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe("Select at least one symptom");
    }
  });

  it("rejects missing symptoms field", () => {
    const result = symptomFormSchema.safeParse({});
    expect(result.success).toBe(false);
  });

  describe("age validation", () => {
    it("accepts valid age", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        age: 25,
      });
      expect(result.success).toBe(true);
    });

    it("accepts null age", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        age: null,
      });
      expect(result.success).toBe(true);
    });

    it("rejects age less than 1", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        age: 0,
      });
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("Age must be at least 1");
      }
    });

    it("rejects age over 150", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        age: 151,
      });
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("Age must be at most 150");
      }
    });

    it("rejects non-integer age", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        age: 25.5,
      });
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0].message).toBe("Age must be a whole number");
      }
    });

    it("rejects non-numeric age string", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        age: "abc",
      });
      expect(result.success).toBe(false);
    });
  });

  describe("gender validation", () => {
    it("accepts valid gender values", () => {
      const genders = ["male", "female", "other"] as const;
      for (const gender of genders) {
        const result = symptomFormSchema.safeParse({
          symptoms: ["Fever"],
          gender,
        });
        expect(result.success).toBe(true);
      }
    });

    it("accepts null gender", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        gender: null,
      });
      expect(result.success).toBe(true);
    });

    it("rejects invalid gender", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        gender: "unknown",
      });
      expect(result.success).toBe(false);
    });
  });

  describe("painLevel validation", () => {
    it("accepts valid pain levels", () => {
      for (let level = 0; level <= 10; level++) {
        const result = symptomFormSchema.safeParse({
          symptoms: ["Fever"],
          painLevel: level,
        });
        expect(result.success).toBe(true);
      }
    });

    it("accepts null pain level", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        painLevel: null,
      });
      expect(result.success).toBe(true);
    });

    it("rejects pain level below 0", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        painLevel: -1,
      });
      expect(result.success).toBe(false);
      if (!result.success) {
        const message = result.error.issues[0].message;
        expect(message).toContain("0");
      }
    });

    it("rejects pain level above 10", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        painLevel: 11,
      });
      expect(result.success).toBe(false);
      if (!result.success) {
        const message = result.error.issues[0].message;
        expect(message).toContain("10");
      }
    });

    it("rejects non-integer pain level", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        painLevel: 5.5,
      });
      expect(result.success).toBe(false);
    });
  });

  describe("existingConditions validation", () => {
    it("accepts array of conditions", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        existingConditions: ["Diabetes", "Asthma"],
      });
      expect(result.success).toBe(true);
    });

    it("defaults to empty array when not provided", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
      });
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.existingConditions).toEqual([]);
      }
    });
  });

  describe("symptomDuration validation", () => {
    it("accepts string duration", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
        symptomDuration: "A few days",
      });
      expect(result.success).toBe(true);
    });

    it("defaults to empty string when not provided", () => {
      const result = symptomFormSchema.safeParse({
        symptoms: ["Fever"],
      });
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.symptomDuration).toBe("");
      }
    });
  });
});
