import { useDashboardStore } from "@/lib/stores/dashboard-store"

describe("dashboard-store", () => {
  beforeEach(() => {
    useDashboardStore.setState({ selectedTimeRange: "6m" })
  })

  it("defaults to 6m time range", () => {
    expect(useDashboardStore.getState().selectedTimeRange).toBe("6m")
  })

  it("sets selected time range", () => {
    useDashboardStore.getState().setSelectedTimeRange("1m")
    expect(useDashboardStore.getState().selectedTimeRange).toBe("1m")
    useDashboardStore.getState().setSelectedTimeRange("1y")
    expect(useDashboardStore.getState().selectedTimeRange).toBe("1y")
  })
})
