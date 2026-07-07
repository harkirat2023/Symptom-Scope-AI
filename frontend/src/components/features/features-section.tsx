import {
  Brain,
  Shield,
  Activity,
  Stethoscope,
  Bell,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Disease Prediction",
    description:
      "Dual ML models (Decision Tree + Random Forest) work together for accurate disease predictions with confidence scoring.",
  },
  {
    icon: Shield,
    title: "Explainable AI",
    description:
      "Every prediction includes top contributing symptoms and feature importance, so you know why a diagnosis was suggested.",
  },
  {
    icon: Activity,
    title: "Severity Assessment",
    description:
      "Instant classification into Mild, Moderate, or Severe categories to help you understand the urgency of your condition.",
  },
  {
    icon: Stethoscope,
    title: "Doctor Recommendations",
    description:
      "Get matched with healthcare providers based on your condition, location, and required medical specialty.",
  },
  {
    icon: Bell,
    title: "Emergency Detection",
    description:
      "Critical conditions trigger immediate alerts with ambulance contact, nearby hospitals, and telemedicine options.",
  },
  {
    icon: BarChart3,
    title: "Health Analytics",
    description:
      "Track your symptom history, prediction trends, and health patterns through an intuitive dashboard with rich visualizations.",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="bg-background py-24">
      <div className="mx-auto max-w-[1440px] px-6">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <h2 className="mb-4">
            Everything You Need for{" "}
            <span className="text-healthcare-blue">Health Intelligence</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            From symptom analysis to emergency detection, SymptomScope AI
            provides a complete healthcare companion experience.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="group rounded-3xl border bg-card p-8 shadow-lg transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
              >
                <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-healthcare-blue/10 group-hover:bg-healthcare-blue/20 transition-colors">
                  <Icon className="h-6 w-6 text-healthcare-blue" />
                </div>
                <h3 className="mb-3 text-xl font-semibold">{feature.title}</h3>
                <p className="leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
