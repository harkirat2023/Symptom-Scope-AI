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

export const SEVERITY_ORDER = ["Severe", "Moderate", "Mild"];
