import { cn } from "@/lib/utils"

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar")
  })

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible")
  })

  it("merges tailwind classes correctly", () => {
    expect(cn("px-4 py-2", "px-6")).toBe("py-2 px-6")
  })

  it("handles clsx array input", () => {
    expect(cn(["a", "b"], "c")).toBe("a b c")
  })

  it("returns empty string for no args", () => {
    expect(cn()).toBe("")
  })
})
