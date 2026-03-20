# Agentic IAM Platform - Architecture Overview

## System Architecture

The Agentic IAM Platform is a layered enterprise application that provides identity intelligence and orchestration capabilities on top of existing IAM systems.

```
┌─────────────────────────────────────────────────────────────┐
│                    Experience Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Dashboard │  │ User     │  │ Approval │  │ Chat/     │  │
│  │          │  │ Search   │  │ Queue    │  │ Assistant │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    API Layer (FastAPI)                       │
│  /users  /comparison  /recommendations  /approvals  /chat   │
├─────────────────────────────────────────────────────────────┤
│              Agent / Reasoning Layer                         │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────┐       │
│  │ IAM Agent     │  │ LLM      │  │ Tool Executor  │       │
│  │ (Orchestrator)│  │ Provider │  │                │       │
│  └──────────────┘  └──────────┘  └────────────────┘       │
├─────────────────────────────────────────────────────────────┤
│              Services Layer                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐       │
│  │ Identity   │  │ Persona    │  │ Comparison     │       │
│  │ Service    │  │ Service    │  │ Service        │       │
│  ├────────────┤  ├────────────┤  ├────────────────┤       │
│  │ Approval   │  │ Action     │  │ Audit          │       │
│  │ Service    │  │ Service    │  │ Service        │       │
│  └────────────┘  └────────────┘  └────────────────┘       │
├─────────────────────────────────────────────────────────────┤
│              Engine Layer                                    │
│  ┌─────────────────┐  ┌──────────────────────────┐        │
│  │ Policy Engine    │  │ Recommendation Engine    │        │
│  │ (Deterministic)  │  │ (Variance + Remediation) │        │
│  └─────────────────┘  └──────────────────────────┘        │
├─────────────────────────────────────────────────────────────┤
│              Data Layer (PostgreSQL + SQLAlchemy)            │
│  Users | Personas | Entitlements | Policies | Audit Logs    │
├─────────────────────────────────────────────────────────────┤
│              Connector Layer                                 │
│  ┌──────────┐  ┌──────┐  ┌───────┐  ┌──────┐             │
│  │ Workday  │  │ AD   │  │ Entra │  │ Apps │             │
│  │ (Mock)   │  │(Mock)│  │(Mock) │  │(Mock)│             │
│  └──────────┘  └──────┘  └───────┘  └──────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Principles

### 1. AI Does NOT Replace Policy
The policy engine is fully deterministic. The AI agent gathers evidence and makes recommendations, but all actions flow through:
- Policy evaluation (deterministic)
- Risk classification
- Approval determination
- Audited execution

### 2. Read-Only First
All source system connectors are read-only by design. Write operations go through the action execution service, which respects the configured action mode.

### 3. Action Modes
- **read_only**: No actions can be executed
- **simulation**: Actions are simulated with detailed output
- **approval_required**: All actions require explicit approval
- **execution**: Low-risk approved actions execute against target systems

### 4. Evidence-Based Reasoning
Every agent response distinguishes:
- **Facts**: Data observed from source systems
- **Policy evaluations**: Deterministic rule outcomes
- **Inferences**: Conclusions drawn from evidence
- **Recommendations**: Suggested actions with risk levels

### 5. Audit Everything
Every request, evidence source, policy result, recommendation, approval, action, and outcome is logged with correlation IDs for end-to-end traceability.

## Data Model

### Identity
- **User**: Normalized identity combining HR, AD, and Entra data
- **UserAttribute**: Flexible key-value attributes from source systems
- **UserLifecycleEvent**: Join/Move/Leave transitions

### Persona & Baseline
- **Persona**: Role-based access profiles
- **PersonaMappingRule**: Conditions that map users to personas
- **PersonaEntitlement**: Expected baseline entitlements per persona

### Entitlements
- **Application**: App catalog with ownership and criticality
- **Group**: AD/Entra groups with risk classification
- **Entitlement**: Normalized entitlement catalog
- **UserEntitlement**: Actual user assignments with exception tracking

### Governance
- **PolicyRule**: Deterministic policy rules
- **PolicyEvaluation**: Audit trail of policy evaluations
- **Recommendation**: Generated remediation recommendations
- **ApprovalRequest**: Approval workflow records
- **ApprovalDecision**: Individual approval decisions
- **ActionRecord**: Execution records with rollback info
- **AuditLog**: Comprehensive audit trail

## Security Model

- JWT-based authentication with role enforcement
- Environment-based configuration (no hardcoded secrets)
- Least-privilege connector design
- Server-side authorization boundaries
- Prompt injection defenses in agent layer
- No raw LLM reasoning exposed to users
- All privileged actions require explicit approval records
