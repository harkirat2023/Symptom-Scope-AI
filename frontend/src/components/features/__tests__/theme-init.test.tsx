import { render } from "@testing-library/react"
import { ThemeInit } from "@/components/features/theme-init"
import { useTheme } from "@/lib/stores/theme-store"

describe("ThemeInit", () => {
  beforeEach(() => {
    document.documentElement.classList.remove("dark")
  })

  it("adds dark class when isDark is true", () => {
    useTheme.setState({ isDark: true })
    render(<ThemeInit />)
    expect(document.documentElement.classList.contains("dark")).toBe(true)
  })

  it("removes dark class when isDark is false", () => {
    useTheme.setState({ isDark: false })
    render(<ThemeInit />)
    expect(document.documentElement.classList.contains("dark")).toBe(false)
  })

  it("renders nothing", () => {
    const { container } = render(<ThemeInit />)
    expect(container.innerHTML).toBe("")
  })
})
