import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "path"

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    css: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: [
        "src/components/features/features-section.tsx",
        "src/components/features/footer.tsx",
        "src/components/features/header.tsx",
        "src/components/features/hero-section.tsx",
        "src/components/features/how-it-works-section.tsx",
        "src/components/features/theme-init.tsx",
        "src/components/ui/alert.tsx",
        "src/components/ui/badge.tsx",
        "src/components/ui/button.tsx",
        "src/components/ui/card.tsx",
        "src/components/ui/input.tsx",
        "src/lib/utils.ts",
        "src/lib/stores/dashboard-store.ts",
        "src/lib/stores/symptom-store.ts",
        "src/lib/stores/theme-store.ts",
      ],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
