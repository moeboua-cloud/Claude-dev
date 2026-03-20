"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { RiskChip } from "../components/ui/RiskChip";
import { EmptyState } from "../components/ui/EmptyState";
import type { AuditLog } from "@/types/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [eventFilter, setEventFilter] = useState("");

  useEffect(() => {
    loadLogs();
  }, [eventFilter]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (eventFilter) params.event_type = eventFilter;
      const result = await api.listAuditLogs(params);
      setLogs(result.items || []);
      setTotal(result.total || 0);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
          <p className="text-sm text-gray-500 mt-1">{total} audit event(s)</p>
        </div>
        <select
          className="input w-48"
          value={eventFilter}
          onChange={(e) => setEventFilter(e.target.value)}
        >
          <option value="">All Events</option>
          <option value="query">Queries</option>
          <option value="agent_response">Agent Responses</option>
          <option value="approval_requested">Approval Requested</option>
          <option value="approval_decision">Approval Decisions</option>
          <option value="action_executed">Actions Executed</option>
          <option value="sync">Sync Events</option>
        </select>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : logs.length === 0 ? (
        <EmptyState message="No audit events recorded yet." />
      ) : (
        <div className="space-y-2">
          {logs.map((log) => (
            <div key={log.id} className="card px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400 w-40 flex-shrink-0">
                  {new Date(log.timestamp).toLocaleString()}
                </span>
                <span className="chip bg-blue-100 text-blue-700 text-xs">
                  {log.event_type}
                </span>
                {log.risk_level && <RiskChip level={log.risk_level} />}
                <span className="text-sm text-gray-700 flex-1 truncate">{log.summary}</span>
                <span className="text-xs text-gray-400">{log.actor}</span>
                <span className="text-xs text-gray-300 font-mono">{log.correlation_id.slice(0, 8)}...</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
