import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { symptomFormSchema, type SymptomFormValues } from "@/lib/validations/symptom-form"
import { SymptomSelectionStep } from "@/components/features/symptom-selection-step"

function TestWrapper({ onComplete }: { onComplete: () => void }) {
  const { control } = useForm<SymptomFormValues>({
    resolver: zodResolver(symptomFormSchema),
    defaultValues: {
      symptoms: [],
      age: null,
      gender: null,
      existingConditions: [],
      symptomDuration: "",
      painLevel: null,
    },
  })

  return (
    <SymptomSelectionStep
      control={control}
      onComplete={onComplete}
    />
  )
}

describe("SymptomSelectionStep", () => {
  it("renders the title", () => {
    render(<TestWrapper onComplete={() => {}} />)
    expect(screen.getByText("What symptoms are you experiencing?")).toBeInTheDocument()
  })

  it("renders search input", () => {
    render(<TestWrapper onComplete={() => {}} />)
    expect(screen.getByPlaceholderText("Search symptoms...")).toBeInTheDocument()
  })

  it("renders available symptoms list", () => {
    render(<TestWrapper onComplete={() => {}} />)
    expect(screen.getByText("Fever")).toBeInTheDocument()
    expect(screen.getByText("Dry Cough")).toBeInTheDocument()
    expect(screen.getByText("Headache")).toBeInTheDocument()
  })

  it("filters symptoms based on search", async () => {
    const user = userEvent.setup()
    render(<TestWrapper onComplete={() => {}} />)

    const searchInput = screen.getByPlaceholderText("Search symptoms...")
    await user.type(searchInput, "fever")

    expect(screen.getByText("Fever")).toBeInTheDocument()
    expect(screen.queryByText("Dry Cough")).not.toBeInTheDocument()
  })

  it("shows no results message when search has no matches", async () => {
    const user = userEvent.setup()
    render(<TestWrapper onComplete={() => {}} />)

    const searchInput = screen.getByPlaceholderText("Search symptoms...")
    await user.type(searchInput, "xyznotasymptom")

    expect(screen.getByText("No symptoms found. Try a different search term.")).toBeInTheDocument()
  })

  it("disables Next button when no symptoms selected", () => {
    render(<TestWrapper onComplete={() => {}} />)
    expect(screen.getByText("Next")).toBeDisabled()
  })

  it("shows symptom count as 0 initially", () => {
    render(<TestWrapper onComplete={() => {}} />)
    expect(screen.getByText("0 symptoms selected")).toBeInTheDocument()
  })
})
