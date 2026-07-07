import Link from "next/link";
import { Activity } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto max-w-[1440px] px-6 py-12">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="mb-4 flex items-center gap-2">
              <Activity className="h-6 w-6 text-healthcare-blue" />
              <span className="text-lg font-bold text-deep-navy dark:text-foreground">
                SymptomScope
              </span>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-muted-foreground">
              AI-powered health intelligence platform. Always consult a
              healthcare professional for medical advice.
            </p>
          </div>

          <div>
            <h4 className="mb-4 text-sm font-semibold">Product</h4>
            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <Link href="#features" className="hover:text-foreground transition-colors">
                Features
              </Link>
              <Link href="#how-it-works" className="hover:text-foreground transition-colors">
                How It Works
              </Link>
              <Link href="/symptom-checker" className="hover:text-foreground transition-colors">
                Symptom Checker
              </Link>
            </div>
          </div>

          <div>
            <h4 className="mb-4 text-sm font-semibold">Legal</h4>
            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <span>Privacy Policy</span>
              <span>Terms of Service</span>
              <span>Medical Disclaimer</span>
            </div>
          </div>
        </div>

        <div className="mt-12 border-t border-border pt-6 text-center text-xs text-muted-foreground">
          &copy; {new Date().getFullYear()} SymptomScope AI. Not a medical
          device. Always consult a qualified healthcare provider.
        </div>
      </div>
    </footer>
  );
}
