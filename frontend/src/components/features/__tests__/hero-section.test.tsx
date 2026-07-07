import { render, screen } from "@testing-library/react"
import { HeroSection } from "@/components/features/hero-section"

describe("HeroSection", () => {
  it("renders the heading", () => {
    render(<HeroSection />)
    expect(
      screen.getByRole("heading").textContent
    ).toContain("AI-Powered Health Intelligence")
  })

  it("renders the description", () => {
    render(<HeroSection />)
    expect(
      screen.getByText(/Receive disease predictions/)
    ).toBeInTheDocument()
  })

  it("renders CTA buttons", () => {
    render(<HeroSection />)
    expect(
      screen.getByText("Start Symptom Assessment")
    ).toBeInTheDocument()
    expect(screen.getByText("Learn More")).toBeInTheDocument()
  })

  it("renders AI badge", () => {
    render(<HeroSection />)
    const badges = screen.getAllByText("AI-Powered Health Intelligence")
    expect(badges.length).toBeGreaterThanOrEqual(1)
  })

  it("renders compliance items", () => {
    render(<HeroSection />)
    expect(screen.getByText("HIPAA Compliant")).toBeInTheDocument()
    expect(screen.getByText("Real-Time Analysis")).toBeInTheDocument()
  })
})
