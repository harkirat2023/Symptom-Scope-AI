import { Search, Brain, ClipboardList, ShieldCheck } from "lucide-react";

const steps = [
  {
    icon: Search,
    title: "Enter Your Symptoms",
    description:
      "Select your symptoms from a searchable list. Add details like age, duration, and pain level for more accurate analysis.",
    step: "01",
  },
  {
    icon: Brain,
    title: "AI Analysis",
    description:
      "Our dual ML models analyze your symptoms against thousands of disease patterns, calculating probabilities and confidence scores.",
    step: "02",
  },
  {
    icon: ClipboardList,
    title: "Review Results",
    description:
      "View your predicted condition, confidence score, severity level, alternative possibilities, and AI explainability insights.",
    step: "03",
  },
  {
    icon: ShieldCheck,
    title: "Take Action",
    description:
      "Get personalized precautions, doctor recommendations, and emergency support if needed — all in one place.",
    step: "04",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="bg-soft-gray py-24 dark:bg-deep-navy/30">
      <div className="mx-auto max-w-[1440px] px-6">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <h2 className="mb-4">
            How It <span className="text-healthcare-blue">Works</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            From symptom entry to actionable health insights in four simple
            steps.
          </p>
        </div>

        <div className="relative grid gap-8 md:grid-cols-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="relative flex flex-col items-center text-center">
                <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-healthcare-blue shadow-lg">
                  <Icon className="h-8 w-8 text-white" />
                </div>
                <span className="mb-2 text-sm font-bold text-healthcare-blue">
                  Step {step.step}
                </span>
                <h3 className="mb-3 text-xl font-semibold">{step.title}</h3>
                <p className="max-w-sm text-muted-foreground">
                  {step.description}
                </p>
                {index < steps.length - 1 && (
                  <div className="absolute right-0 top-8 hidden h-0.5 w-[calc(100%-4rem)] bg-gradient-to-r from-healthcare-blue/40 to-transparent md:block" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
