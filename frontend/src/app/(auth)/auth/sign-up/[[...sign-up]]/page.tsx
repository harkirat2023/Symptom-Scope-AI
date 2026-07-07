import { Suspense } from "react"
import { SignUp } from "@clerk/nextjs";

export const dynamic = 'force-dynamic';

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-soft-gray px-4">
      <Suspense fallback={<div className="text-center">Loading…</div>}>
        <SignUp
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl rounded-3xl",
            },
          }}
        />
      </Suspense>
    </div>
  );
}
