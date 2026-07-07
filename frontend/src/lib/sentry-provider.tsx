"use client";

import { useEffect, type ReactNode } from "react";
import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

export function SentryProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    if (!SENTRY_DSN || typeof window === "undefined") return;
    if ((window as unknown as Record<string, boolean>).__sentry_initialized) return;

    Sentry.init({
      dsn: SENTRY_DSN,
      environment: process.env.NODE_ENV,
      tracesSampleRate: 0.1,
      integrations: [Sentry.browserTracingIntegration()],
    });

    (window as unknown as Record<string, boolean>).__sentry_initialized = true;
  }, []);

  return <>{children}</>;
}
