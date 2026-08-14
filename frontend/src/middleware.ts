import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse, type NextRequest } from "next/server";

const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/history(.*)",
  "/reports(.*)",
  "/settings(.*)",
  "/symptom-checker(.*)",
  "/results(.*)",
]);

// Determine whether Clerk configuration is present.
const hasClerkConfig = Boolean(process.env.CLERK_JWKS_URL || process.env.CLERK_ISSUER);

// If Clerk is configured, use the official clerkMiddleware pattern. The
// middleware will invoke the afterAuth hook where we protect specific routes.
// If Clerk is not configured, provide a safe fallback middleware that does not
// expose protected routes in production and allows previews in non-production.
const middleware = hasClerkConfig
  ? clerkMiddleware({
      async afterAuth(auth, req) {
        if (isProtectedRoute(req)) {
          await auth.protect();
        }
      },
    })
  : (async (req: NextRequest) => {
      if (isProtectedRoute(req)) {
        if (process.env.NODE_ENV === "production") {
          return new Response("Authentication provider not configured", { status: 500 });
        }
        return NextResponse.next();
      }
      return NextResponse.next();
    });

export default middleware;

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
