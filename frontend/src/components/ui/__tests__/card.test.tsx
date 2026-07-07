import { render, screen } from "@testing-library/react"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card"

describe("Card", () => {
  it("renders card with children", () => {
    render(<Card><CardContent>Content</CardContent></Card>)
    expect(screen.getByText("Content")).toBeInTheDocument()
  })

  it("renders with default size", () => {
    render(<Card data-testid="card">Content</Card>)
    expect(screen.getByTestId("card")).toHaveAttribute("data-size", "default")
  })

  it("renders with sm size", () => {
    render(<Card size="sm" data-testid="card">Content</Card>)
    expect(screen.getByTestId("card")).toHaveAttribute("data-size", "sm")
  })

  it("renders CardHeader", () => {
    render(<Card><CardHeader data-testid="header">Header</CardHeader></Card>)
    expect(screen.getByTestId("header")).toBeInTheDocument()
  })

  it("renders CardTitle", () => {
    render(<Card><CardTitle>Title</CardTitle></Card>)
    expect(screen.getByText("Title")).toBeInTheDocument()
  })

  it("renders CardDescription", () => {
    render(<Card><CardDescription>Desc</CardDescription></Card>)
    expect(screen.getByText("Desc")).toBeInTheDocument()
  })

  it("renders CardFooter", () => {
    render(<Card><CardFooter>Footer</CardFooter></Card>)
    expect(screen.getByText("Footer")).toBeInTheDocument()
  })

  it("accepts additional className on card", () => {
    render(<Card className="custom" data-testid="card">Content</Card>)
    expect(screen.getByTestId("card")).toHaveClass("custom")
  })
})
