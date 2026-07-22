export interface TooltipPayloadEntry {
  name: string;
  value: number | string;
  color: string;
}

export interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

export const severityColors: Record<string, string> = {
  Mild: "#22c55e",
  Moderate: "#f59e0b",
  Severe: "#ef4444",
};

export const severityBadgeColors: Record<string, string> = {
  Mild: "bg-success/10 text-success border-success/20",
  Moderate: "bg-warning/10 text-warning border-warning/20",
  Severe: "bg-destructive/10 text-destructive border-destructive/20",
};

export const SEVERITY_ORDER = ["Severe", "Moderate", "Mild"];
