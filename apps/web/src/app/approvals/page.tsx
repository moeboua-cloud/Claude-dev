"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { RiskChip } from "../components/ui/RiskChip";
import { StatusChip } from "../components/ui/StatusChip";
import { EmptyState } from "../components/ui/EmptyState";
import type { ApprovalRequest } from "@/types/api";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const result = await api.listApprovals();
      setApprovals(Array.isArray(result) ? result : []);
    } catch {
      setApprovals([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (id: string, decision: string) => {
    try {
      await api.decideApproval(id, decision, `${decision} by analyst`);
      if (decision === "approved") {
        await api.executeAction(id);
      }
      loadApprovals();
    } catch {
      // handle error
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Approval Queue</h1>

      {approvals.length === 0 ? (
        <EmptyState message="No pending approvals. Submit recommendations for approval first." />
      ) : (
        <div className="space-y-3">
          {approvals.map((ap) => (
            <div key={ap.id} className="card p-5">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <RiskChip level={ap.risk_level} />
                    <StatusChip status={ap.status} />
                    <span className="chip bg-gray-100 text-gray-700">{ap.action_type}</span>
                  </div>
                  <h3 className="font-medium text-gray-900">
                    {ap.action_details?.entitlement_name as string || "Action"} - {ap.action_type}
                  </h3>
                  <div className="flex gap-4 mt-2 text-xs text-gray-500">
                    <span>Requested by: {ap.requested_by}</span>
                    <span>Required approvers: {ap.required_approvers.join(", ")}</span>
                    <span>Created: {new Date(ap.created_at).toLocaleString()}</span>
                  </div>
                </div>
                {ap.status === "pending" && (
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleDecision(ap.id, "approved")}
                      className="btn-primary"
                    >
                      Approve & Execute
                    </button>
                    <button
                      onClick={() => handleDecision(ap.id, "rejected")}
                      className="btn-danger"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
