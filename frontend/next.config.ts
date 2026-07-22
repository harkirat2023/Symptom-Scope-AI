import type { NextConfig } from "next";

const cspValue = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://clerk.accounts.dev https://*.clerk.accounts.dev https://*.accounts.dev https://challenges.cloudflare.com",
  "worker-src 'self' blob:",
  "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
  "img-src 'self' data: blob: https://img.clerk.com https://fastapi.tiangolo.com",
  "font-src 'self' data:",
  "connect-src 'self' https://clerk.accounts.dev https://*.clerk.accounts.dev https://*.accounts.dev https://clerk-telemetry.com https://challenges.cloudflare.com https://*.sentry.io http://localhost:* ws://localhost:* https://us.i.posthog.com",
  "frame-src 'self' https://clerk.accounts.dev https://*.clerk.accounts.dev https://*.accounts.dev https://challenges.cloudflare.com",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

const nextConfig: NextConfig = {
  output: "standalone",
  compress: true,
  poweredByHeader: false,
  reactStrictMode: true,

  typescript: {
    ignoreBuildErrors: true,
  },

  images: {
    minimumCacheTTL: 60 * 60 * 24,
  },

  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Content-Security-Policy", value: cspValue },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), interest-cohort=()",
          },
        ],
      },
    ];
  },
};

export default nextConfig;

