"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { RiskChip } from "../components/ui/RiskChip";
import Link from "next/link";

interface DashboardStats {
  totalUsers: number;
  movers: number;
  pendingRecommendations: number;
  pendingApprovals: number;
  recentAudit: number;
  synced: boolean;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStats = async () => {
    try {
      const [users, recs, approvals, audit] = await Promise.all([
        api.searchUsers().catch(() => []),
        api.listRecommendations().catch(() => ({ items: [], total: 0 })),
        api.listApprovals().catch(() => []),
        api.listAuditLogs({ limit: "10" }).catch(() => ({ items: [], total: 0 })),
      ]);

      setStats({
        totalUsers: users.length,
        movers: users.filter((u: any) => u.lifecycle_state === "mover").length,
        pendingRecommendations: recs.total || 0,
        pendingApprovals: Array.isArray(approvals) ? approvals.length : 0,
        recentAudit: audit.total || 0,
        synced: users.length > 0,
      });
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const runSync = async () => {
    setSyncing(true);
    try {
      await api.runFullSync();
      await loadStats();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">IAM Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Identity intelligence and access management overview</p>
        </div>
        <button
          onClick={runSync}
          disabled={syncing}
          className="btn-primary"
        >
          {syncing ? "Syncing..." : "Sync Data"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm">
          {error}
        </div>
      )}

      {!stats?.synced && (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-6 text-sm">
          No data found. Click &quot;Sync Data&quot; to ingest mock data from source systems.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Users" value={stats?.totalUsers || 0} href="/users" />
        <StatCard title="Movers" value={stats?.movers || 0} href="/users?lifecycle_state=mover" color="orange" />
        <StatCard title="Pending Recommendations" value={stats?.pendingRecommendations || 0} href="/recommendations" color="blue" />
        <StatCard title="Pending Approvals" value={stats?.pendingApprovals || 0} href="/approvals" color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link href="/chat" className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors">
              <div className="font-medium text-sm">Ask the IAM Assistant</div>
              <div className="text-xs text-gray-500 mt-1">
                &quot;Why does Sarah not have Epic access?&quot;
              </div>
            </Link>
            <Link href="/users" className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors">
              <div className="font-medium text-sm">Search Users</div>
              <div className="text-xs text-gray-500 mt-1">Look up users and compare access</div>
            </Link>
            <Link href="/recommendations" className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors">
              <div className="font-medium text-sm">Review Recommendations</div>
              <div className="text-xs text-gray-500 mt-1">Process pending access recommendations</div>
            </Link>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">System Status</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Environment</span>
              <span className="font-medium">Local (Mock)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Action Mode</span>
              <RiskChip level="medium" />
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Connector Mode</span>
              <span className="font-medium">Mock Providers</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Audit Events</span>
              <span className="font-medium">{stats?.recentAudit || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, href, color = "gray" }: { title: string; value: number; href: string; color?: string }) {
  const colors: Record<string, string> = {
    gray: "border-l-gray-400",
    orange: "border-l-orange-400",
    blue: "border-l-blue-400",
    purple: "border-l-purple-400",
  };
  return (
    <Link href={href} className={`card p-4 border-l-4 ${colors[color]} hover:shadow-md transition-shadow`}>
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </Link>
  );
}
