"use client";

import { clsx } from "clsx";

const riskColors: Record<string, string> = {
  low: "chip-low",
  medium: "chip-medium",
  high: "chip-high",
  critical: "chip-critical",
};

export function RiskChip({ level }: { level: string }) {
  return (
    <span className={clsx("chip", riskColors[level] || "chip-low")}>
      {level.toUpperCase()}
    </span>
  );
}
