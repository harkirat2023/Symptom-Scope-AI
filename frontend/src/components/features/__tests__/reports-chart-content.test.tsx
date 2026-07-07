import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { toast } from "sonner"

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

import ReportsChartContent from "@/components/features/reports-chart-content"

const mockReport = {
  generated_at: "2026-06-11T00:00:00Z",
  total_predictions: 5,
  most_common_disease: "Influenza",
  avg_confidence: 85.5,
  severe_count: 1,
  severity_distribution: { Mild: 3, Moderate: 1, Severe: 1 },
  predictions: [
    {
      id: "1",
      user_id: "user-1",
      symptoms: ["Fever", "Cough"],
      prediction: "Influenza",
      confidence: 85.5,
      severity: "Moderate",
      timestamp: "2026-06-10T00:00:00Z",
    },
  ],
}

const defaultProps = {
  report: mockReport,
  analytics: undefined,
  gridColor: "#e2e8f0",
  textColor: "#0f172a",
  userId: "user-123",
  getToken: async () => "test-token",
}

describe("ReportsChartContent", () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it("renders health summary card", () => {
    render(<ReportsChartContent {...defaultProps} />)
    expect(screen.getByText("Health Summary")).toBeInTheDocument()
  })

  it("renders Download CSV button", () => {
    render(<ReportsChartContent {...defaultProps} />)
    expect(screen.getByText("Download CSV")).toBeInTheDocument()
  })

  it("renders Download PDF button", () => {
    render(<ReportsChartContent {...defaultProps} />)
    expect(screen.getByText("Download PDF")).toBeInTheDocument()
  })

  it("shows error toast when userId is missing on export", async () => {
    const user = userEvent.setup()
    const toastError = vi.spyOn(toast, "error")
    render(<ReportsChartContent {...defaultProps} userId="" />)

    await user.click(screen.getByText("Download CSV"))
    expect(toastError).toHaveBeenCalledWith(
      "You must be logged in to export reports"
    )
  })

  it("downloads CSV on button click", async () => {
    const user = userEvent.setup()
    const blob = new Blob(["csv content"], { type: "text/csv" })
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: async () => blob,
    })

    render(<ReportsChartContent {...defaultProps} />)
    await user.click(screen.getByText("Download CSV"))

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/export/csv/user-123"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    )
  })

  it("downloads PDF on button click", async () => {
    const user = userEvent.setup()
    const blob = new Blob(["pdf content"], { type: "application/pdf" })
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: async () => blob,
    })

    render(<ReportsChartContent {...defaultProps} />)
    await user.click(screen.getByText("Download PDF"))

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/export/pdf/user-123"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    )
  })

  it("shows error toast on failed export", async () => {
    const user = userEvent.setup()
    const toastError = vi.spyOn(toast, "error")
    mockFetch.mockResolvedValueOnce({ ok: false })

    render(<ReportsChartContent {...defaultProps} />)
    await user.click(screen.getByText("Download CSV"))

    expect(toastError).toHaveBeenCalledWith(
      "Failed to download CSV report"
    )
  })

  it("shows success toast on successful download", async () => {
    const user = userEvent.setup()
    const toastSuccess = vi.spyOn(toast, "success")
    const blob = new Blob(["csv content"], { type: "text/csv" })
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: async () => blob,
    })

    render(<ReportsChartContent {...defaultProps} />)
    await user.click(screen.getByText("Download CSV"))

    expect(toastSuccess).toHaveBeenCalledWith(
      "CSV report downloaded successfully"
    )
  })

  it("disables buttons while exporting", async () => {
    const user = userEvent.setup()
    const blob = new Blob(["csv content"], { type: "text/csv" })

    let resolveBlob: (v: Blob) => void
    const blobPromise = new Promise<Blob>((resolve) => {
      resolveBlob = resolve
    })

    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: async () => blobPromise,
    })

    render(<ReportsChartContent {...defaultProps} />)
    const csvButton = screen.getByRole("button", { name: /download csv/i })

    user.click(csvButton)

    const downloadingButton = await screen.findByRole("button", { name: /downloading/i })
    expect(downloadingButton).toBeDisabled()

    resolveBlob!(blob)
  })
})
