import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

const mockGetToken = vi.fn()
const mockUseAuth = vi.fn()
const mockUseQuery = vi.fn()

vi.mock("@clerk/nextjs", () => ({
  useAuth: () => mockUseAuth(),
}))

vi.mock("@tanstack/react-query", () => ({
  useQuery: (opts: { enabled?: boolean }) => mockUseQuery(opts),
}))

import { EmergencyActionPanel } from "@/components/features/emergency-action-panel"

describe("EmergencyActionPanel", () => {
  beforeEach(() => {
    mockGetToken.mockResolvedValue("test-token")
    mockUseAuth.mockReturnValue({ getToken: mockGetToken })
    mockUseQuery.mockReturnValue({
      data: { hospitals: [], total: 0 },
      isLoading: false,
    })
  })

  it("renders the section heading", () => {
    render(<EmergencyActionPanel />)
    expect(screen.getByText("Recommended Actions")).toBeInTheDocument()
  })

  it("renders Call Ambulance button", () => {
    render(<EmergencyActionPanel />)
    const button = screen.getByRole("button", { name: /call ambulance/i })
    expect(button).toBeInTheDocument()
  })

  it("renders Nearby Hospitals button", () => {
    render(<EmergencyActionPanel />)
    const button = screen.getByRole("button", { name: /nearby hospitals/i })
    expect(button).toBeInTheDocument()
  })

  it("renders Teleconsultation button", () => {
    render(<EmergencyActionPanel />)
    const button = screen.getByRole("button", { name: /teleconsultation/i })
    expect(button).toBeInTheDocument()
  })

  it("has accessible role group", () => {
    render(<EmergencyActionPanel />)
    expect(
      screen.getByRole("group", { name: /emergency action options/i })
    ).toBeInTheDocument()
  })

  it("opens hospitals dialog when Nearby Hospitals is clicked", async () => {
    const user = userEvent.setup()
    render(<EmergencyActionPanel />)

    await user.click(screen.getByRole("button", { name: /nearby hospitals/i }))
    expect(
      screen.getByRole("dialog", { name: /nearby hospitals/i })
    ).toBeInTheDocument()
  })

  it("opens teleconsultation dialog when Teleconsultation is clicked", async () => {
    const user = userEvent.setup()
    render(<EmergencyActionPanel />)

    await user.click(screen.getByRole("button", { name: /teleconsultation/i }))
    expect(screen.getByRole("dialog", { name: /teleconsultation/i })).toBeInTheDocument()
  })

  it("displays predicted disease in teleconsultation dialog when provided", async () => {
    const user = userEvent.setup()
    render(<EmergencyActionPanel predictedDisease="Influenza" />)

    await user.click(screen.getByRole("button", { name: /teleconsultation/i }))
    expect(screen.getByText(/related to Influenza/i)).toBeInTheDocument()
  })
})
