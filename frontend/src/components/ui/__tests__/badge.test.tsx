import { render, screen } from "@testing-library/react"
import { Badge } from "@/components/ui/badge"

describe("Badge", () => {
  it("renders children", () => {
    render(<Badge>New</Badge>)
    expect(screen.getByText("New")).toBeInTheDocument()
  })

  it("applies default variant classes", () => {
    render(<Badge data-testid="badge">Default</Badge>)
    const badge = screen.getByTestId("badge")
    expect(badge.className).toContain("bg-primary")
  })

  it("applies destructive variant", () => {
    render(<Badge variant="destructive" data-testid="badge">Destructive</Badge>)
    const badge = screen.getByTestId("badge")
    expect(badge.className).toContain("bg-destructive")
  })

  it("applies outline variant", () => {
    render(<Badge variant="outline" data-testid="badge">Outline</Badge>)
    const badge = screen.getByTestId("badge")
    expect(badge.className).toContain("border-border")
  })

  it("accepts additional className", () => {
    render(<Badge className="custom" data-testid="badge">Badge</Badge>)
    expect(screen.getByTestId("badge").className).toContain("custom")
  })
})
