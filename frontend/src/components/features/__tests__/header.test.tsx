import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Header } from "@/components/features/header"
import { useTheme } from "@/lib/stores/theme-store"

const mockUseAuth = vi.fn()

vi.mock("@clerk/nextjs", () => ({
  useAuth: () => mockUseAuth(),
  UserButton: () => <div data-testid="user-button" />,
}))

describe("Header", () => {
  beforeEach(() => {
    useTheme.setState({ isDark: false })
    mockUseAuth.mockReturnValue({ isSignedIn: false })
  })

  it("renders the brand name", () => {
    render(<Header />)
    expect(screen.getByText("SymptomScope")).toBeInTheDocument()
  })

  it("renders navigation links", () => {
    render(<Header />)
    expect(screen.getByText("Features")).toBeInTheDocument()
    expect(screen.getByText("How It Works")).toBeInTheDocument()
  })

  it("shows sign in when not authenticated", () => {
    render(<Header />)
    expect(screen.getByText("Sign In")).toBeInTheDocument()
    expect(screen.getByText("Get Started")).toBeInTheDocument()
  })

  it("shows dashboard link when signed in", () => {
    mockUseAuth.mockReturnValue({ isSignedIn: true })
    render(<Header />)
    expect(screen.getByText("Dashboard")).toBeInTheDocument()
  })

  it("toggles theme on button click", async () => {
    render(<Header />)
    const toggleButton = screen.getByRole("button", {
      name: /switch to dark mode/i,
    })
    await userEvent.click(toggleButton)
    expect(useTheme.getState().isDark).toBe(true)
  })

  it("shows sun icon in dark mode", () => {
    useTheme.setState({ isDark: true })
    render(<Header />)
    expect(
      screen.getByRole("button", { name: /switch to light mode/i })
    ).toBeInTheDocument()
  })
})
