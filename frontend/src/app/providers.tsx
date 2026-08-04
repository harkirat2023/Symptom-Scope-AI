"use client";

import dynamic from "next/dynamic";
import { ClerkProvider } from "@/lib/clerk-provider";
import { QueryProvider } from "@/lib/query-provider";
import { ThemeInit } from "@/components/features/theme-init";
import { Toaster } from "@/components/ui/sonner";

const KeyboardShortcutsHelp = dynamic(
  () => import("@/components/features/keyboard-shortcuts").then((m) => m.KeyboardShortcutsHelp),
  { ssr: false }
);

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <QueryProvider>
        <ThemeInit />
        <Toaster />
        <KeyboardShortcutsHelp />
        {children}
      </QueryProvider>
    </ClerkProvider>
  );
}
