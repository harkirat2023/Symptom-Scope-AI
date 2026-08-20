import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";
import type { NextFetchEvent, NextRequest } from "next/server";

const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/history(.*)",
  "/reports(.*)",
  "/settings(.*)",
  "/symptom-checker(.*)",
  "/results(.*)",
  "/recovery-plan(.*)",
  "/reminders(.*)",
]);

// Wrap Clerk middleware invocation in a try/catch so that deployments without
// Clerk configuration (e.g., preview environments) do not fail the middleware
// step. If Clerk is not configured, middleware becomes a no-op and protected
// routes should be guarded server-side where necessary.
export default async function middleware(request: NextRequest, event: NextFetchEvent) {
  try {
    const handler = clerkMiddleware(async (auth, req) => {
      if (isProtectedRoute(req)) {
        await auth.protect();
      }
    });
    return await handler(request, event);
  } catch (e) {
    // If Clerk throws (missing config, runtime issues), allow the request to
    // continue so the site can still serve public pages. Log via console so
    // Vercel/Edge logs capture the event.
    console.warn("Clerk middleware skipped due to configuration error:", e);
    return NextResponse.next();
  }
}

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
