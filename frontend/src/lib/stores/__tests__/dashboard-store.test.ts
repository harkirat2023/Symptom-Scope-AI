import { useDashboardStore } from "@/lib/stores/dashboard-store"

describe("dashboard-store", () => {
  beforeEach(() => {
    useDashboardStore.setState({ sidebarOpen: true, selectedTimeRange: "6m" })
  })

  it("starts with sidebar open", () => {
    expect(useDashboardStore.getState().sidebarOpen).toBe(true)
  })

  it("defaults to 6m time range", () => {
    expect(useDashboardStore.getState().selectedTimeRange).toBe("6m")
  })

  it("toggles sidebar", () => {
    useDashboardStore.getState().toggleSidebar()
    expect(useDashboardStore.getState().sidebarOpen).toBe(false)
    useDashboardStore.getState().toggleSidebar()
    expect(useDashboardStore.getState().sidebarOpen).toBe(true)
  })

  it("sets sidebar open", () => {
    useDashboardStore.getState().setSidebarOpen(false)
    expect(useDashboardStore.getState().sidebarOpen).toBe(false)
    useDashboardStore.getState().setSidebarOpen(true)
    expect(useDashboardStore.getState().sidebarOpen).toBe(true)
  })

  it("sets selected time range", () => {
    useDashboardStore.getState().setSelectedTimeRange("1m")
    expect(useDashboardStore.getState().selectedTimeRange).toBe("1m")
    useDashboardStore.getState().setSelectedTimeRange("1y")
    expect(useDashboardStore.getState().selectedTimeRange).toBe("1y")
  })
})
