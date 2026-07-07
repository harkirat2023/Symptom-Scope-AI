import { render, screen } from "@testing-library/react"
import { Footer } from "@/components/features/footer"

describe("Footer", () => {
  it("renders brand name", () => {
    render(<Footer />)
    expect(screen.getByText("SymptomScope")).toBeInTheDocument()
  })

  it("renders Product links", () => {
    render(<Footer />)
    expect(screen.getByText("Features")).toBeInTheDocument()
    expect(screen.getByText("How It Works")).toBeInTheDocument()
    expect(screen.getByText("Symptom Checker")).toBeInTheDocument()
  })

  it("renders Legal section", () => {
    render(<Footer />)
    expect(screen.getByText("Privacy Policy")).toBeInTheDocument()
    expect(screen.getByText("Terms of Service")).toBeInTheDocument()
    expect(screen.getByText("Medical Disclaimer")).toBeInTheDocument()
  })

  it("renders medical disclaimer text", () => {
    render(<Footer />)
    expect(
      screen.getByText(
        /AI-powered health intelligence platform/
      )
    ).toBeInTheDocument()
  })

  it("renders Product heading", () => {
    render(<Footer />)
    expect(screen.getByText("Product")).toBeInTheDocument()
  })

  it("renders Legal heading", () => {
    render(<Footer />)
    expect(screen.getByText("Legal")).toBeInTheDocument()
  })
})
