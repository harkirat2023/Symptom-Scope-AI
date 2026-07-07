import { create } from "zustand";

interface DashboardState {
  sidebarOpen: boolean;
  selectedTimeRange: "1m" | "3m" | "6m" | "1y";
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSelectedTimeRange: (range: DashboardState["selectedTimeRange"]) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  sidebarOpen: true,
  selectedTimeRange: "6m",
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSelectedTimeRange: (range) => set({ selectedTimeRange: range }),
}));
