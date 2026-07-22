"use client";

import dynamic from "next/dynamic";

const DashboardLayoutClient = dynamic(() => import("./dashboard-layout-client"), { ssr: false });

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardLayoutClient>{children}</DashboardLayoutClient>;
}
