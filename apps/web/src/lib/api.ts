const API_BASE = "/api/v1";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Users
  searchUsers: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi<any[]>(`/users${qs}`);
  },
  getUser: (id: string) => fetchApi<any>(`/users/${id}`),
  getUserAccessGraph: (id: string) => fetchApi<any>(`/users/${id}/access-graph`),

  // Comparison
  compareAccess: (userId: string) => fetchApi<any>(`/comparison/${userId}`),

  // Recommendations
  listRecommendations: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi<any>(`/recommendations${qs}`);
  },
  generateRecommendations: (userId: string) =>
    fetchApi<any[]>(`/recommendations/${userId}/generate`, { method: "POST" }),

  // Approvals
  listApprovals: () => fetchApi<any[]>("/approvals"),
  requestApproval: (recommendationId: string) =>
    fetchApi<any>(`/approvals/request/${recommendationId}`, { method: "POST" }),
  decideApproval: (approvalId: string, decision: string, reason?: string) =>
    fetchApi<any>(`/approvals/${approvalId}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision, reason }),
    }),
  executeAction: (approvalId: string) =>
    fetchApi<any>(`/approvals/${approvalId}/execute`, { method: "POST" }),

  // Audit
  listAuditLogs: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchApi<any>(`/audit${qs}`);
  },
  getAuditTimeline: (correlationId: string) =>
    fetchApi<any>(`/audit/timeline/${correlationId}`),

  // Chat
  chat: (message: string, context?: Record<string, unknown>) =>
    fetchApi<any>("/chat", {
      method: "POST",
      body: JSON.stringify({ message, context }),
    }),

  // Sync
  runFullSync: () => fetchApi<any>("/sync/full", { method: "POST" }),

  // Health
  health: () => fetchApi<any>("/health"),
};
