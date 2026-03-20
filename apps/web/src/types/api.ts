export interface User {
  id: string;
  employee_id: string;
  email: string;
  display_name: string;
  first_name: string;
  last_name: string;
  job_title: string | null;
  job_family: string | null;
  sub_job_family: string | null;
  department: string | null;
  cost_center: string | null;
  legal_entity: string | null;
  region: string | null;
  location: string | null;
  manager_employee_id: string | null;
  worker_type: string;
  lifecycle_state: string;
  hire_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserEntitlement {
  id: string;
  entitlement_name: string;
  entitlement_type: string;
  source: string;
  is_privileged: boolean;
  is_exception: boolean;
  risk_level: string;
  granted_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
}

export interface PersonaMatch {
  persona_id: string;
  persona_name: string;
  match_score: number;
  matched_conditions: Record<string, string>;
}

export interface LifecycleEvent {
  id: string;
  event_type: string;
  previous_state: Record<string, string> | null;
  new_state: Record<string, string> | null;
  effective_date: string;
  detected_at: string;
}

export interface UserDetail extends User {
  entitlements: UserEntitlement[];
  matched_personas: PersonaMatch[];
  lifecycle_events: LifecycleEvent[];
}

export interface EntitlementVariance {
  entitlement_name: string;
  entitlement_type: string;
  status: "missing" | "excess" | "matched" | "exception";
  risk_level: string;
  is_privileged: boolean;
  expected_by_persona: string | null;
  evidence: Record<string, unknown>;
}

export interface AccessComparison {
  user_id: string;
  user_display_name: string;
  matched_personas: string[];
  total_expected: number;
  total_actual: number;
  missing_entitlements: EntitlementVariance[];
  excess_entitlements: EntitlementVariance[];
  matched_entitlements: EntitlementVariance[];
  exception_entitlements: EntitlementVariance[];
  overall_compliance_score: number;
  risk_summary: {
    critical_excess: number;
    high_excess: number;
    missing_required: number;
    privileged_excess: number;
  };
}

export interface Recommendation {
  id: string;
  user_id: string;
  user_display_name: string | null;
  recommendation_type: string;
  category: string;
  title: string;
  description: string;
  evidence: Record<string, unknown>;
  risk_level: string;
  confidence_score: number;
  status: string;
  requires_approval: boolean;
  suggested_action: Record<string, unknown> | null;
  created_at: string;
}

export interface ApprovalRequest {
  id: string;
  correlation_id: string;
  recommendation_id: string;
  requested_by: string;
  target_user_id: string;
  action_type: string;
  action_details: Record<string, unknown>;
  risk_level: string;
  required_approvers: string[];
  status: string;
  created_at: string;
  expires_at: string | null;
}

export interface AuditLog {
  id: string;
  correlation_id: string;
  event_type: string;
  actor: string;
  actor_role: string | null;
  target_type: string | null;
  target_id: string | null;
  summary: string;
  details: Record<string, unknown> | null;
  evidence_sources: string[] | null;
  policy_results: unknown[] | null;
  risk_level: string | null;
  outcome: string | null;
  timestamp: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
}

export interface ChatResponse {
  correlation_id: string;
  answer: string;
  intent: string;
  evidence: Array<{
    source: string;
    description: string;
    data: Record<string, unknown>;
    confidence: number;
  }>;
  policy_evaluations: unknown[];
  recommendations: unknown[];
  risk_level: string | null;
  requires_action: boolean;
  suggested_actions: unknown[];
  timestamp: string;
}
