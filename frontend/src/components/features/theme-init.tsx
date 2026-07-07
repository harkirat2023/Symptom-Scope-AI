"use client";

import { useEffect } from "react";
import { useTheme } from "@/lib/stores/theme-store";

export function ThemeInit() {
  const { isDark } = useTheme();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  return null;
}
