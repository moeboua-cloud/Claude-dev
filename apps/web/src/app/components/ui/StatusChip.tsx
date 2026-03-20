"use client";

import { clsx } from "clsx";

const statusStyles: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-blue-100 text-blue-800",
  rejected: "bg-red-100 text-red-800",
  executed: "bg-purple-100 text-purple-800",
  simulated: "bg-indigo-100 text-indigo-800",
  mover: "bg-orange-100 text-orange-800",
  leaver: "bg-red-100 text-red-800",
  pre_hire: "bg-gray-100 text-gray-800",
  terminated: "bg-gray-100 text-gray-600",
  missing: "bg-red-100 text-red-800",
  excess: "bg-orange-100 text-orange-800",
  matched: "bg-green-100 text-green-800",
  exception: "bg-purple-100 text-purple-800",
};

export function StatusChip({ status }: { status: string }) {
  return (
    <span className={clsx("chip", statusStyles[status] || "bg-gray-100 text-gray-700")}>
      {status.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}
