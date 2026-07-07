import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { symptomFormSchema, type SymptomFormValues } from "@/lib/validations/symptom-form"
import { DetailsStep } from "@/components/features/details-step"

function TestWrapper({ onBack, onStartAnalysis }: { onBack: () => void; onStartAnalysis: () => void }) {
  const { register, control, formState: { errors } } = useForm<SymptomFormValues>({
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
    <DetailsStep
      register={register}
      errors={errors}
      control={control}
      onBack={onBack}
      onStartAnalysis={onStartAnalysis}
    />
  )
}

describe("DetailsStep", () => {
  it("renders the title", () => {
    render(<TestWrapper onBack={() => {}} onStartAnalysis={() => {}} />)
    expect(screen.getByText("Additional Details")).toBeInTheDocument()
  })

  it("renders age input", () => {
    render(<TestWrapper onBack={() => {}} onStartAnalysis={() => {}} />)
    expect(screen.getByLabelText("Age")).toBeInTheDocument()
  })

  it("renders gender select", () => {
    render(<TestWrapper onBack={() => {}} onStartAnalysis={() => {}} />)
    expect(screen.getByLabelText("Gender")).toBeInTheDocument()
  })

  it("renders duration select", () => {
    render(<TestWrapper onBack={() => {}} onStartAnalysis={() => {}} />)
    expect(screen.getByLabelText("How long have you had these symptoms?")).toBeInTheDocument()
  })

  it("renders pain level slider", () => {
    render(<TestWrapper onBack={() => {}} onStartAnalysis={() => {}} />)
    expect(screen.getByText("Pain Level: Not specified")).toBeInTheDocument()
  })

  it("renders Back and Start Analysis buttons", () => {
    render(<TestWrapper onBack={() => {}} onStartAnalysis={() => {}} />)
    expect(screen.getByText("Back")).toBeInTheDocument()
    expect(screen.getByText("Start Analysis")).toBeInTheDocument()
  })

  it("calls onBack when Back button clicked", async () => {
    const user = userEvent.setup()
    const onBack = vi.fn()
    render(<TestWrapper onBack={onBack} onStartAnalysis={() => {}} />)

    await user.click(screen.getByText("Back"))
    expect(onBack).toHaveBeenCalledTimes(1)
  })

  it("calls onStartAnalysis when Start Analysis clicked", async () => {
    const user = userEvent.setup()
    const onStartAnalysis = vi.fn()
    render(<TestWrapper onBack={() => {}} onStartAnalysis={onStartAnalysis} />)

    await user.click(screen.getByText("Start Analysis"))
    expect(onStartAnalysis).toHaveBeenCalledTimes(1)
  })
})
