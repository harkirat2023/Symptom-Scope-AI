import { render, screen } from "@testing-library/react"
import { FeaturesSection } from "@/components/features/features-section"

describe("FeaturesSection", () => {
  it("renders the section with id", () => {
    render(<FeaturesSection />)
    const section = document.getElementById("features")
    expect(section).toBeInTheDocument()
  })

  it("renders all feature titles", () => {
    render(<FeaturesSection />)
    expect(screen.getByText("AI Disease Prediction")).toBeInTheDocument()
    expect(screen.getByText("Explainable AI")).toBeInTheDocument()
    expect(screen.getByText("Severity Assessment")).toBeInTheDocument()
    expect(screen.getByText("Doctor Recommendations")).toBeInTheDocument()
    expect(screen.getByText("Emergency Detection")).toBeInTheDocument()
    expect(screen.getByText("Health Analytics")).toBeInTheDocument()
  })

  it("renders feature descriptions", () => {
    render(<FeaturesSection />)
    expect(
      screen.getByText(/Dual ML models/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Every prediction includes top contributing symptoms/)
    ).toBeInTheDocument()
  })

  it("renders the heading", () => {
    render(<FeaturesSection />)
    expect(
      screen.getByText("Health Intelligence")
    ).toBeInTheDocument()
  })
})
