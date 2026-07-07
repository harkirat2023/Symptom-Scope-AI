import { render, screen } from "@testing-library/react"
import {
  Alert,
  AlertTitle,
  AlertDescription,
  AlertAction,
} from "@/components/ui/alert"

describe("Alert", () => {
  it("renders alert with role", () => {
    render(<Alert>Alert content</Alert>)
    expect(screen.getByRole("alert")).toBeInTheDocument()
  })

  it("renders AlertTitle", () => {
    render(<Alert><AlertTitle>Warning</AlertTitle></Alert>)
    expect(screen.getByText("Warning")).toBeInTheDocument()
  })

  it("renders AlertDescription", () => {
    render(<Alert><AlertDescription>Description text</AlertDescription></Alert>)
    expect(screen.getByText("Description text")).toBeInTheDocument()
  })

  it("renders AlertAction", () => {
    render(<Alert><AlertAction data-testid="action">Action</AlertAction></Alert>)
    expect(screen.getByTestId("action")).toBeInTheDocument()
  })

  it("applies destructive variant", () => {
    render(<Alert variant="destructive" data-testid="alert">Destructive</Alert>)
    const alert = screen.getByTestId("alert")
    expect(alert.className).toContain("text-destructive")
  })

  it("accepts additional className", () => {
    render(<Alert className="custom" data-testid="alert">Alert</Alert>)
    expect(screen.getByTestId("alert").className).toContain("custom")
  })
})
