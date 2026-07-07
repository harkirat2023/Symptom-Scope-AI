import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Input } from "@/components/ui/input"

describe("Input", () => {
  it("renders input element", () => {
    render(<Input placeholder="Enter text" />)
    expect(screen.getByPlaceholderText("Enter text")).toBeInTheDocument()
  })

  it("accepts type prop", () => {
    render(<Input type="email" data-testid="input" />)
    expect(screen.getByTestId("input")).toHaveAttribute("type", "email")
  })

  it("handles value changes", async () => {
    const handleChange = vi.fn()
    render(<Input onChange={handleChange} />)
    const input = screen.getByRole("textbox")
    await userEvent.type(input, "a")
    expect(handleChange).toHaveBeenCalled()
  })

  it("applies additional className", () => {
    render(<Input className="custom" data-testid="input" />)
    expect(screen.getByTestId("input").className).toContain("custom")
  })

  it("forwards disabled prop", () => {
    render(<Input disabled data-testid="input" />)
    expect(screen.getByTestId("input")).toBeDisabled()
  })
})
