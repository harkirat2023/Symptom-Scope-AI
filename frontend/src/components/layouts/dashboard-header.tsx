"use client";

import Link from "next/link";
import { Menu, Stethoscope } from "lucide-react";
import { UserButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

interface DashboardHeaderProps {
  onMenuClick: () => void;
}

export function DashboardHeader({ onMenuClick }: DashboardHeaderProps) {
  return (
    <header className="sticky top-0 z-50 flex h-14 items-center gap-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 lg:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
        aria-label="Open sidebar navigation"
      >
        <Menu className="size-5" />
      </Button>

      <Link href="/dashboard" className="flex items-center gap-2 font-semibold" aria-label="SymptomScope AI Dashboard Home">
        <Stethoscope className="size-5 text-primary" aria-hidden="true" />
        <span>SymptomScope</span>
      </Link>

      <div className="flex-1" />

      <UserButton
        appearance={{
          elements: {
            avatarBox: "size-8",
          },
        }}
      />
    </header>
  );
}
