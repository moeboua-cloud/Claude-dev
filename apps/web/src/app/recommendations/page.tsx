"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { RiskChip } from "../components/ui/RiskChip";
import { StatusChip } from "../components/ui/StatusChip";
import { EmptyState } from "../components/ui/EmptyState";
import type { Recommendation } from "@/types/api";

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecs();
  }, []);

  const loadRecs = async () => {
    setLoading(true);
    try {
      const result = await api.listRecommendations();
      setRecs(result.items || []);
      setTotal(result.total || 0);
    } catch {
      setRecs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestApproval = async (recId: string) => {
    try {
      await api.requestApproval(recId);
      loadRecs();
    } catch {
      // handle error
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recommendations</h1>
          <p className="text-sm text-gray-500 mt-1">{total} pending recommendation(s)</p>
        </div>
      </div>

      {recs.length === 0 ? (
        <EmptyState message="No pending recommendations. Generate recommendations from a user's profile." />
      ) : (
        <div className="space-y-3">
          {recs.map((rec) => (
            <div key={rec.id} className="card p-5">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <RiskChip level={rec.risk_level} />
                    <StatusChip status={rec.status} />
                    <span className="chip bg-gray-100 text-gray-700">{rec.recommendation_type}</span>
                    <span className="text-xs text-gray-500">{rec.category.replace(/_/g, " ")}</span>
                  </div>
                  <h3 className="font-medium text-gray-900">{rec.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    <span>Confidence: {Math.round(rec.confidence_score * 100)}%</span>
                    <span>Created: {new Date(rec.created_at).toLocaleString()}</span>
                  </div>
                </div>
                {rec.status === "pending" && rec.requires_approval && (
                  <button
                    onClick={() => handleRequestApproval(rec.id)}
                    className="btn-primary ml-4"
                  >
                    Request Approval
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
