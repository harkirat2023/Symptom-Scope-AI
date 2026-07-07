import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Button } from "@/components/ui/button"

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole("button")).toHaveTextContent("Click me")
  })

  it("applies default variant classes", () => {
    render(<Button>Default</Button>)
    const button = screen.getByRole("button")
    expect(button).toHaveClass("bg-primary")
  })

  it("applies outline variant", () => {
    render(<Button variant="outline">Outline</Button>)
    const button = screen.getByRole("button")
    expect(button).toHaveClass("border-border")
  })

  it("applies size classes", () => {
    render(<Button size="sm">Small</Button>)
    const button = screen.getByRole("button")
    expect(button).toHaveClass("h-7")
  })

  it("handles click events", async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    await userEvent.click(screen.getByRole("button"))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it("accepts additional className", () => {
    render(<Button className="custom-class">Styled</Button>)
    expect(screen.getByRole("button")).toHaveClass("custom-class")
  })

  it("renders as disabled", () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole("button")).toBeDisabled()
  })
})
