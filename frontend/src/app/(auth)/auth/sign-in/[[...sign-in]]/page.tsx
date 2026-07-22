import { Suspense } from "react"
import { SignIn } from "@clerk/nextjs";

export const dynamic = 'force-dynamic';

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-soft-gray px-4">
      <Suspense fallback={<div className="text-center">Loading…</div>}>
        <SignIn
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl rounded-3xl",
              socialButtonsBlockButton: "hidden",
              dividerRow: "hidden",
            },
          }}
        />
      </Suspense>
    </div>
  );
}
