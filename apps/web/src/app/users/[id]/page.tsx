"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { RiskChip } from "../../components/ui/RiskChip";
import { StatusChip } from "../../components/ui/StatusChip";
import type { UserDetail, AccessComparison, Recommendation } from "@/types/api";

export default function UserDetailPage() {
  const params = useParams();
  const userId = params.id as string;

  const [user, setUser] = useState<UserDetail | null>(null);
  const [comparison, setComparison] = useState<AccessComparison | null>(null);
  const [recommendations, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"access" | "comparison" | "recommendations" | "lifecycle">("access");

  useEffect(() => {
    loadData();
  }, [userId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [u, c] = await Promise.all([
        api.getUser(userId),
        api.compareAccess(userId).catch(() => null),
      ]);
      setUser(u);
      setComparison(c);
    } catch {
      // handle error
    } finally {
      setLoading(false);
    }
  };

  const generateRecs = async () => {
    try {
      const recs = await api.generateRecommendations(userId);
      setRecs(recs);
      setActiveTab("recommendations");
    } catch {
      // handle error
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!user) return <div className="text-red-500">User not found</div>;

  return (
    <div>
      {/* User header */}
      <div className="card p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">{user.display_name}</h1>
            <p className="text-gray-500 mt-1">{user.email}</p>
            <div className="flex gap-4 mt-3 text-sm text-gray-600">
              <span><strong>ID:</strong> {user.employee_id}</span>
              <span><strong>Dept:</strong> {user.department}</span>
              <span><strong>Title:</strong> {user.job_title}</span>
              <span><strong>Region:</strong> {user.region}</span>
            </div>
            <div className="flex gap-2 mt-3">
              <StatusChip status={user.lifecycle_state} />
              <span className="chip bg-gray-100 text-gray-700">{user.worker_type}</span>
              {user.matched_personas?.map((p) => (
                <span key={p.persona_id} className="chip bg-blue-100 text-blue-800">
                  {p.persona_name} ({Math.round(p.match_score * 100)}%)
                </span>
              ))}
            </div>
          </div>
          <button onClick={generateRecs} className="btn-primary">
            Generate Recommendations
          </button>
        </div>
      </div>

      {/* Compliance summary */}
      {comparison && (
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold">{Math.round(comparison.overall_compliance_score * 100)}%</p>
            <p className="text-xs text-gray-500">Compliance</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{comparison.matched_entitlements.length}</p>
            <p className="text-xs text-gray-500">Matched</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-red-600">{comparison.missing_entitlements.length}</p>
            <p className="text-xs text-gray-500">Missing</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-orange-600">{comparison.excess_entitlements.length}</p>
            <p className="text-xs text-gray-500">Excess</p>
          </div>
          <div className="card p-4 text-center">
            <p className="text-2xl font-bold text-purple-600">{comparison.exception_entitlements.length}</p>
            <p className="text-xs text-gray-500">Exceptions</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b mb-6">
        <nav className="flex gap-6">
          {(["access", "comparison", "recommendations", "lifecycle"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors capitalize ${
                activeTab === tab
                  ? "border-primary-600 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === "access" && (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Entitlement</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Source</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Risk</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Flags</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {user.entitlements.map((ent) => (
                <tr key={ent.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{ent.entitlement_name}</td>
                  <td className="px-4 py-3 text-gray-600">{ent.entitlement_type}</td>
                  <td className="px-4 py-3 text-gray-600">{ent.source}</td>
                  <td className="px-4 py-3"><RiskChip level={ent.risk_level} /></td>
                  <td className="px-4 py-3">
                    {ent.is_privileged && <span className="chip chip-critical mr-1">Privileged</span>}
                    {ent.is_exception && <span className="chip bg-purple-100 text-purple-800">Exception</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "comparison" && comparison && (
        <div className="space-y-6">
          {comparison.missing_entitlements.length > 0 && (
            <div>
              <h3 className="font-semibold text-red-700 mb-2">Missing Baseline Entitlements</h3>
              <div className="card overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-red-50 border-b"><tr>
                    <th className="text-left px-4 py-2 font-medium">Entitlement</th>
                    <th className="text-left px-4 py-2 font-medium">Expected By</th>
                    <th className="text-left px-4 py-2 font-medium">Risk</th>
                  </tr></thead>
                  <tbody className="divide-y">
                    {comparison.missing_entitlements.map((e, i) => (
                      <tr key={i}><td className="px-4 py-2">{e.entitlement_name}</td>
                      <td className="px-4 py-2 text-gray-600">{e.expected_by_persona}</td>
                      <td className="px-4 py-2"><RiskChip level={e.risk_level} /></td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {comparison.excess_entitlements.length > 0 && (
            <div>
              <h3 className="font-semibold text-orange-700 mb-2">Excess Entitlements</h3>
              <div className="card overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-orange-50 border-b"><tr>
                    <th className="text-left px-4 py-2 font-medium">Entitlement</th>
                    <th className="text-left px-4 py-2 font-medium">Risk</th>
                    <th className="text-left px-4 py-2 font-medium">Privileged</th>
                  </tr></thead>
                  <tbody className="divide-y">
                    {comparison.excess_entitlements.map((e, i) => (
                      <tr key={i}><td className="px-4 py-2">{e.entitlement_name}</td>
                      <td className="px-4 py-2"><RiskChip level={e.risk_level} /></td>
                      <td className="px-4 py-2">{e.is_privileged ? "Yes" : "No"}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {comparison.matched_entitlements.length > 0 && (
            <div>
              <h3 className="font-semibold text-green-700 mb-2">Matched Baseline Entitlements</h3>
              <div className="card overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-green-50 border-b"><tr>
                    <th className="text-left px-4 py-2 font-medium">Entitlement</th>
                    <th className="text-left px-4 py-2 font-medium">Persona</th>
                  </tr></thead>
                  <tbody className="divide-y">
                    {comparison.matched_entitlements.map((e, i) => (
                      <tr key={i}><td className="px-4 py-2">{e.entitlement_name}</td>
                      <td className="px-4 py-2 text-gray-600">{e.expected_by_persona}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "recommendations" && (
        <div className="space-y-3">
          {recommendations.length === 0 ? (
            <div className="text-center text-gray-500 text-sm py-8">
              Click &quot;Generate Recommendations&quot; to analyze this user&apos;s access.
            </div>
          ) : (
            recommendations.map((rec) => (
              <div key={rec.id} className="card p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <RiskChip level={rec.risk_level} />
                      <span className="chip bg-gray-100 text-gray-700">{rec.recommendation_type}</span>
                      <span className="text-xs text-gray-500">{rec.category}</span>
                    </div>
                    <h4 className="font-medium">{rec.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      Confidence: {Math.round(rec.confidence_score * 100)}%
                    </p>
                  </div>
                  {rec.requires_approval && (
                    <button
                      className="btn-secondary text-xs"
                      onClick={() => api.requestApproval(rec.id)}
                    >
                      Request Approval
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === "lifecycle" && (
        <div className="space-y-3">
          {user.lifecycle_events.length === 0 ? (
            <div className="text-center text-gray-500 text-sm py-8">No lifecycle events recorded.</div>
          ) : (
            user.lifecycle_events.map((evt) => (
              <div key={evt.id} className="card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <StatusChip status={evt.event_type} />
                  <span className="text-xs text-gray-500">
                    {new Date(evt.effective_date).toLocaleDateString()}
                  </span>
                </div>
                {evt.previous_state && (
                  <div className="text-sm">
                    <strong className="text-gray-500">From:</strong>{" "}
                    {Object.entries(evt.previous_state).map(([k, v]) => `${k}: ${v}`).join(", ")}
                  </div>
                )}
                {evt.new_state && (
                  <div className="text-sm">
                    <strong className="text-gray-500">To:</strong>{" "}
                    {Object.entries(evt.new_state).map(([k, v]) => `${k}: ${v}`).join(", ")}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
