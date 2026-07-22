"use client";

import { ClerkProvider as ClerkProviderBase } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { useTheme } from "@/lib/stores/theme-store";
import type { ReactNode } from "react";

export function ClerkProvider({ children }: { children: ReactNode }) {
  const isDark = useTheme((state) => state.isDark);

  return (
    <ClerkProviderBase
      signInUrl="/auth/sign-in"
      signUpUrl="/auth/sign-up"
      appearance={{
        theme: isDark ? dark : undefined,
        variables: {
          colorPrimary: "#2563eb",
          colorForeground: isDark ? "#f8fafc" : "#0f172a",
          colorBackground: isDark ? "#020617" : "#ffffff",
          colorInput: isDark ? "#0f172a" : "#ffffff",
          colorInputForeground: isDark ? "#f8fafc" : "#0f172a",
          borderRadius: "0.75rem",
        },
      }}
    >
      {children}
    </ClerkProviderBase>
  );
}
