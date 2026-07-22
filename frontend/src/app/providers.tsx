"use client";

import dynamic from "next/dynamic";
import { ClerkProvider } from "@/lib/clerk-provider";
import { QueryProvider } from "@/lib/query-provider";
import { PostHogProvider } from "@/lib/posthog-provider";
import { SentryProvider } from "@/lib/sentry-provider";
import { ThemeInit } from "@/components/features/theme-init";
import { ChatWidget } from "@/components/features/chat/chat-widget";
import { Toaster } from "@/components/ui/sonner";

const KeyboardShortcutsHelp = dynamic(
  () => import("@/components/features/keyboard-shortcuts").then((m) => m.KeyboardShortcutsHelp),
  { ssr: false }
);

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <QueryProvider>
        <SentryProvider>
          <PostHogProvider>
            <ThemeInit />
            <Toaster />
            <KeyboardShortcutsHelp />
            {children}
            <ChatWidget />
          </PostHogProvider>
        </SentryProvider>
      </QueryProvider>
    </ClerkProvider>
  );
}
