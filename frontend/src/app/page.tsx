import { Header } from "@/components/features/header";
import { HeroSection } from "@/components/features/hero-section";
import { FeaturesSection } from "@/components/features/features-section";
import { HowItWorksSection } from "@/components/features/how-it-works-section";
import { Footer } from "@/components/features/footer";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
      </main>
      <Footer />
    </div>
  );
}
