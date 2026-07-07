import { useTheme } from "@/lib/stores/theme-store"

beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove("dark")
  useTheme.setState({ isDark: false })
})

describe("theme-store", () => {
  it("initializes isDark from localStorage", () => {
    localStorage.setItem("theme", "dark")
    const fresh = useTheme.getState()
    expect(fresh.isDark).toBe(false)
  })

  it("toggles theme from light to dark", () => {
    useTheme.setState({ isDark: false })
    useTheme.getState().toggleTheme()
    expect(useTheme.getState().isDark).toBe(true)
    expect(localStorage.getItem("theme")).toBe("dark")
    expect(document.documentElement.classList.contains("dark")).toBe(true)
  })

  it("toggles theme from dark to light", () => {
    useTheme.setState({ isDark: true })
    useTheme.getState().toggleTheme()
    expect(useTheme.getState().isDark).toBe(false)
    expect(localStorage.getItem("theme")).toBe("light")
    expect(document.documentElement.classList.contains("dark")).toBe(false)
  })

  it("setIsDark sets dark mode", () => {
    useTheme.getState().setIsDark(true)
    expect(useTheme.getState().isDark).toBe(true)
    expect(localStorage.getItem("theme")).toBe("dark")
    expect(document.documentElement.classList.contains("dark")).toBe(true)
  })

  it("setIsDark sets light mode", () => {
    useTheme.getState().setIsDark(true)
    useTheme.getState().setIsDark(false)
    expect(useTheme.getState().isDark).toBe(false)
    expect(localStorage.getItem("theme")).toBe("light")
    expect(document.documentElement.classList.contains("dark")).toBe(false)
  })
})
