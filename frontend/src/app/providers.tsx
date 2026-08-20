"use client";

import { ClerkProvider } from "@/lib/clerk-provider";
import { QueryProvider } from "@/lib/query-provider";
import { ThemeInit } from "@/components/features/theme-init";
import { Toaster } from "@/components/ui/sonner";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <QueryProvider>
        <ThemeInit />
        <Toaster />
        {children}
      </QueryProvider>
    </ClerkProvider>
  );
}