import { render, screen } from "@testing-library/react"
import { HowItWorksSection } from "@/components/features/how-it-works-section"

describe("HowItWorksSection", () => {
  it("renders the section with id", () => {
    render(<HowItWorksSection />)
    const section = document.getElementById("how-it-works")
    expect(section).toBeInTheDocument()
  })

  it("renders all step titles", () => {
    render(<HowItWorksSection />)
    expect(screen.getByText("Enter Your Symptoms")).toBeInTheDocument()
    expect(screen.getByText("AI Analysis")).toBeInTheDocument()
    expect(screen.getByText("Review Results")).toBeInTheDocument()
    expect(screen.getByText("Take Action")).toBeInTheDocument()
  })

  it("renders step numbers", () => {
    render(<HowItWorksSection />)
    expect(screen.getByText("Step 01")).toBeInTheDocument()
    expect(screen.getByText("Step 02")).toBeInTheDocument()
    expect(screen.getByText("Step 03")).toBeInTheDocument()
    expect(screen.getByText("Step 04")).toBeInTheDocument()
  })

  it("renders heading", () => {
    render(<HowItWorksSection />)
    expect(screen.getByText("How It")).toBeInTheDocument()
    expect(screen.getByText("Works")).toBeInTheDocument()
  })

  it("renders description text", () => {
    render(<HowItWorksSection />)
    expect(
      screen.getByText(/From symptom entry to actionable health insights/)
    ).toBeInTheDocument()
  })
})
