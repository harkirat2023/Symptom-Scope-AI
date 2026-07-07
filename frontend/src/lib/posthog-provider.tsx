"use client";

import { Suspense, useEffect, type ReactNode } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import posthog from "posthog-js";

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com";

function PostHogTracker({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!POSTHOG_KEY || typeof window === "undefined") return;
    if (!(window as unknown as Record<string, boolean>).__posthog_initialized) {
      posthog.init(POSTHOG_KEY, {
        api_host: POSTHOG_HOST,
        capture_pageview: false,
        loaded: () => {
          (window as unknown as Record<string, boolean>).__posthog_initialized = true;
        },
      });
    }
  }, []);

  useEffect(() => {
    if (POSTHOG_KEY && pathname) {
      const url = searchParams?.toString()
        ? `${pathname}?${searchParams.toString()}`
        : pathname;
      posthog.capture("$pageview", { url });
    }
  }, [pathname, searchParams]);

  return <>{children}</>;
}

export function PostHogProvider({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={null}>
      <PostHogTracker>{children}</PostHogTracker>
    </Suspense>
  );
}
