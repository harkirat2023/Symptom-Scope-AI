import { create } from "zustand";

interface DashboardState {
  selectedTimeRange: "1m" | "3m" | "6m" | "1y";
  setSelectedTimeRange: (range: DashboardState["selectedTimeRange"]) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  selectedTimeRange: "6m",
  setSelectedTimeRange: (range) => set({ selectedTimeRange: range }),
}));
