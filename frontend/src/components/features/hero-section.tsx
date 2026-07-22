"use client";

import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { ArrowRight, Shield, Brain, Activity, Heart, TrendingUp, CalendarDays } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

function MedicalIllustration() {
  return (
    <svg viewBox="0 0 240 340" className="h-56 w-auto" xmlns="http://www.w3.org/2000/svg" aria-label="Medical body illustration with vital organs">
      <defs>
        <linearGradient id="bodyGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.08" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0.02" />
        </linearGradient>
        <linearGradient id="pulseGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#2563eb" stopOpacity="0" />
          <stop offset="40%" stopColor="#2563eb" stopOpacity="0.8" />
          <stop offset="60%" stopColor="#14b8a6" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <circle cx="120" cy="32" r="22" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" fill="url(#bodyGrad)" />
      <line x1="120" y1="54" x2="120" y2="130" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="68" y1="80" x2="120" y2="95" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="172" y1="80" x2="120" y2="95" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <rect x="88" y="130" width="64" height="70" rx="14" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" fill="url(#bodyGrad)" />
      <line x1="120" y1="200" x2="120" y2="250" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="72" y1="230" x2="120" y2="240" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="168" y1="230" x2="120" y2="240" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="120" y1="250" x2="100" y2="315" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="120" y1="250" x2="140" y2="315" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="68" y1="80" x2="36" y2="115" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />
      <line x1="172" y1="80" x2="204" y2="115" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground/30" />

      <circle cx="120" cy="32" r="14" fill="#2563eb1a" stroke="#2563eb33" strokeWidth="1" />
      <path d="M114 28 Q120 24 126 28 Q130 34 126 38 Q120 42 114 38 Q110 34 114 28Z" fill="#2563eb22" className="dark:opacity-40" />

      <ellipse cx="120" cy="82" rx="8" ry="6" fill="#ef44441a" stroke="#ef444433" strokeWidth="1" />
      <path d="M115 82 Q120 78 125 82" fill="none" stroke="#ef444466" strokeWidth="0.8" />

      <ellipse cx="120" cy="150" rx="18" ry="12" fill="#14b8a61a" stroke="#14b8a633" strokeWidth="1" />
      <ellipse cx="108" cy="148" rx="7" ry="9" fill="#14b8a610" stroke="#14b8a620" strokeWidth="0.8" />
      <ellipse cx="132" cy="148" rx="7" ry="9" fill="#14b8a610" stroke="#14b8a620" strokeWidth="0.8" />
      <path d="M106 152 Q120 148 134 152" fill="none" stroke="#14b8a644" strokeWidth="0.6" />

      <path d="M115 172 Q120 168 125 172" fill="none" stroke="#f59e0b44" strokeWidth="1" />
      <path d="M115 178 Q120 174 125 178" fill="none" stroke="#f59e0b44" strokeWidth="1" />

      <circle cx="84" cy="22" r="3.5" fill="#2563eb44" />
      <circle cx="156" cy="22" r="3.5" fill="#2563eb44" />
      <circle cx="96" cy="12" r="2" fill="#14b8a644" />
      <circle cx="144" cy="12" r="2" fill="#14b8a644" />
      <circle cx="120" cy="48" r="1.5" fill="#2563eb66" />

      <circle cx="70" cy="145" r="2" fill="#22c55e66" />
      <circle cx="170" cy="145" r="2" fill="#22c55e66" />
      <circle cx="78" cy="160" r="1.5" fill="#22c55e66" />
      <circle cx="162" cy="160" r="1.5" fill="#22c55e66" />

      <rect x="170" y="50" width="30" height="4" rx="2" fill="url(#pulseGrad)" opacity="0.7">
        <animate attributeName="x" from="170" to="-10" dur="3s" repeatCount="indefinite" />
      </rect>
      <rect x="170" y="58" width="24" height="4" rx="2" fill="url(#pulseGrad)" opacity="0.5">
        <animate attributeName="x" from="170" to="-10" dur="3.5s" repeatCount="indefinite" />
      </rect>

      <g opacity="0.4">
        <text x="120" y="332" textAnchor="middle" fontSize="9" className="fill-muted-foreground/50" fontFamily="Inter, sans-serif">AI-Powered Health Scan</text>
      </g>
    </svg>
  );
}

function DashboardPreview() {
  const bars = [
    { label: "This Week", value: 78, color: "from-healthcare-blue to-medical-teal" },
    { label: "Last Week", value: 65, color: "from-healthcare-blue/60 to-medical-teal/60" },
  ];

  return (
    <div className="rounded-2xl border bg-card p-4 shadow-lg w-full max-w-xs">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="size-7 rounded-lg bg-gradient-to-br from-healthcare-blue to-medical-teal flex items-center justify-center">
            <Activity className="size-3.5 text-white" />
          </div>
          <span className="text-xs font-semibold">Dashboard Preview</span>
        </div>
        <span className="text-[10px] text-muted-foreground">Live</span>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="relative size-12 shrink-0">
            <svg viewBox="0 0 36 36" className="size-12 -rotate-90">
              <defs>
                <linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#2563eb" />
                  <stop offset="100%" stopColor="#14b8a6" />
                </linearGradient>
              </defs>
              <circle cx="18" cy="18" r="15.5" fill="none" stroke="currentColor" strokeWidth="2" className="text-muted/20" />
              <circle cx="18" cy="18" r="15.5" fill="none" stroke="url(#scoreGrad)" strokeWidth="2" strokeDasharray="97.4" strokeDashoffset="17.5" strokeLinecap="round" />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-medical-teal">82</span>
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium">Health Score</p>
            <p className="text-[10px] text-muted-foreground">Up 8% from last month</p>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-lg bg-muted/50 p-2">
          <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-warning/10 text-[10px] font-bold text-warning">!</span>
          <div className="min-w-0 flex-1">
            <p className="text-[11px] font-medium leading-tight">Influenza</p>
            <div className="flex items-center gap-2">
              <span className="text-[9px] text-muted-foreground">Confidence</span>
              <span className="text-[10px] font-semibold text-medical-teal">92%</span>
              <span className="text-[9px] px-1 rounded bg-warning/10 text-warning">Moderate</span>
            </div>
          </div>
        </div>

        <div className="space-y-1.5">
          {bars.map((bar) => (
            <div key={bar.label} className="flex items-center gap-2">
              <span className="w-16 text-[9px] text-muted-foreground shrink-0">{bar.label}</span>
              <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                <div className={cn("h-full rounded-full bg-gradient-to-r", bar.color)} style={{ width: `${bar.value}%` }} />
              </div>
              <span className="text-[10px] font-medium w-6 text-right">{bar.value}</span>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <div className="flex-1 rounded-lg border p-1.5 text-center">
            <Heart className="size-3 mx-auto mb-0.5 text-destructive" />
            <p className="text-[9px] text-muted-foreground">Heart</p>
            <p className="text-[10px] font-semibold text-success">Normal</p>
          </div>
          <div className="flex-1 rounded-lg border p-1.5 text-center">
            <TrendingUp className="size-3 mx-auto mb-0.5 text-medical-teal" />
            <p className="text-[9px] text-muted-foreground">Trend</p>
            <p className="text-[10px] font-semibold text-medical-teal">Stable</p>
          </div>
          <div className="flex-1 rounded-lg border p-1.5 text-center">
            <CalendarDays className="size-3 mx-auto mb-0.5 text-primary" />
            <p className="text-[9px] text-muted-foreground">Checks</p>
            <p className="text-[10px] font-semibold text-primary">12</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background to-soft-gray dark:from-background dark:to-deep-navy/50">
      <div className="mx-auto max-w-[1440px] px-6 py-24 md:py-32">
        <motion.div
          className="grid items-center gap-12 md:grid-cols-2"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="flex flex-col gap-8">
            <motion.div
              className="inline-flex w-fit items-center gap-2 rounded-full border border-healthcare-blue/20 bg-healthcare-blue/5 px-4 py-1.5"
              variants={itemVariants}
            >
              <Brain className="h-4 w-4 text-healthcare-blue" />
              <span className="text-sm font-medium text-healthcare-blue">
                AI-Powered Health Intelligence
              </span>
            </motion.div>

            <motion.h1
              className="text-4xl font-bold leading-tight tracking-tight md:text-[56px]"
              variants={itemVariants}
            >
              Understand Your Symptoms with{" "}
              <span className="text-healthcare-blue">
                AI-Powered Health Intelligence
              </span>
            </motion.h1>

            <motion.p
              className="max-w-lg text-lg leading-relaxed text-muted-foreground"
              variants={itemVariants}
            >
              Receive disease predictions, confidence scores, and healthcare
              guidance in seconds. Powered by advanced machine learning and
              explainable AI.
            </motion.p>

            <motion.div
              className="flex flex-wrap gap-4"
              variants={itemVariants}
            >
              <Link
                href="/symptom-checker"
                className={cn(
                  buttonVariants({ variant: "default", size: "lg" }),
                  "h-[52px] rounded-2xl px-8 text-base"
                )}
              >
                Start Symptom Assessment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="#how-it-works"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "h-[52px] rounded-2xl px-8 text-base"
                )}
              >
                Learn More
              </Link>
            </motion.div>

            <motion.div
              className="flex flex-wrap gap-6 text-sm text-muted-foreground"
              variants={itemVariants}
            >
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-success" />
                HIPAA Compliant
              </div>
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-medical-teal" />
                Real-Time Analysis
              </div>
            </motion.div>
          </div>

          <motion.div
            className="relative hidden md:block"
            variants={itemVariants}
          >
            <div className="relative flex items-center justify-center">
              <div className="h-[420px] w-[420px] rounded-full bg-gradient-to-br from-healthcare-blue/15 via-medical-teal/8 to-transparent blur-3xl" />
              <div className="absolute flex flex-col items-center gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center rounded-2xl border bg-card p-3 shadow-lg">
                    <MedicalIllustration />
                  </div>
                  <div className="space-y-3">
                    <DashboardPreview />
                  </div>
                </div>
                <div className="rounded-2xl border bg-card px-5 py-3 shadow-lg w-full max-w-xs">
                  <div className="flex items-center gap-3">
                    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-warning/10 text-sm font-bold text-warning">
                      !
                    </span>
                    <div className="flex items-center gap-4 flex-1">
                      <div>
                        <p className="text-sm font-semibold">Influenza Detected</p>
                        <p className="text-xs text-muted-foreground">Severity: Moderate</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-medical-teal">92%</p>
                        <p className="text-[10px] text-muted-foreground">confidence</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
