# Agentic IAM Platform

An enterprise-grade Identity and Access Management intelligence and orchestration platform that sits above existing IAM systems to provide identity troubleshooting, entitlement intelligence, persona-based access analysis, mover anomaly detection, and human-in-the-loop remediation.

## Architecture

```
Experience Layer    →  React/Next.js UI (Dashboard, Users, Approvals, Chat)
API Layer           →  FastAPI REST API with JWT auth
Agent Layer         →  LLM-powered reasoning with tool calling
Services Layer      →  Identity, Persona, Comparison, Approval, Action, Audit
Engine Layer        →  Deterministic Policy Engine + Recommendation Engine
Data Layer          →  PostgreSQL with SQLAlchemy async ORM
Connector Layer     →  Mock adapters for Workday, AD, Entra ID
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Key Features

- **Identity Troubleshooting**: Natural language queries like "Why does Sarah not have Epic access?"
- **Persona-Based Baseline**: Map users to personas and compute expected entitlements
- **Access Variance Analysis**: Compare actual vs expected access with compliance scoring
- **Mover Detection**: Identify stale access from department transfers
- **Recommendation Engine**: Generate remediation recommendations with risk classification
- **Approval Workflow**: Route high-risk changes through approval chains
- **Simulation Mode**: Safe execution with detailed simulation output
- **Full Audit Trail**: Correlation ID-based end-to-end traceability
- **Deterministic Policy Engine**: AI does NOT replace policy - all actions flow through deterministic checks

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for manual setup)
- Node.js 20+ (for manual setup)

### Docker Compose (recommended)

```bash
docker compose up -d
python scripts/seed.py
open http://localhost:3000
```

### Manual Setup

```bash
# Terminal 1: Start infrastructure
docker run -d --name iam-db -e POSTGRES_DB=agentic_iam -e POSTGRES_USER=iam_user -e POSTGRES_PASSWORD=iam_pass -p 5432:5432 postgres:16-alpine
docker run -d --name iam-redis -p 6379:6379 redis:7-alpine

# Terminal 2: Start API
cd apps/api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Terminal 3: Start UI
cd apps/web
npm install
npm run dev

# Terminal 4: Seed data
pip install httpx
python scripts/seed.py
```

## Repository Structure

```
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── agent/          # LLM agent, tools, providers
│   │   │   ├── connectors/     # Source system adapters (mock)
│   │   │   ├── core/           # Config, database, security, correlation
│   │   │   ├── engine/         # Policy engine, recommendation engine
│   │   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── routers/        # API endpoints
│   │   │   ├── schemas/        # Pydantic request/response schemas
│   │   │   └── services/       # Business logic services
│   │   └── tests/              # Pytest test suite
│   └── web/                    # Next.js frontend
│       └── src/
│           ├── app/            # Pages and components
│           ├── lib/            # API client
│           └── types/          # TypeScript types
├── packages/
│   ├── shared-types/           # Cross-package type definitions
│   ├── policy-engine/          # Extractable policy engine
│   ├── agent-core/             # Extractable agent framework
│   └── connector-sdk/          # Connector development kit
├── docs/                       # Architecture and setup documentation
├── scripts/                    # Seed and utility scripts
├── docker-compose.yml          # Local development stack
└── README.md
```

## Demo Scenarios

See [docs/demo-scenarios.md](docs/demo-scenarios.md) for 10 pre-configured scenarios including:

1. New hire missing baseline access (Priya Patel)
2. Mover retaining old department access (David Kim)
3. Excess privileged group membership (John Smith)
4. Contractor with PAM access - policy violation (Bob External)
5. Exception entitlement needing review (Lisa Johnson)
6. Natural language troubleshooting via chat
7. Approval workflow for recommended removal
8. Simulated action execution
9. Full audit timeline with correlation IDs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/health | System health check |
| GET | /api/v1/users | Search users |
| GET | /api/v1/users/{id} | User detail with entitlements |
| GET | /api/v1/users/{id}/access-graph | Full access graph |
| GET | /api/v1/comparison/{user_id} | Compare actual vs expected access |
| GET | /api/v1/recommendations | List pending recommendations |
| POST | /api/v1/recommendations/{user_id}/generate | Generate recommendations |
| GET | /api/v1/approvals | List pending approvals |
| POST | /api/v1/approvals/request/{rec_id} | Create approval request |
| POST | /api/v1/approvals/{id}/decide | Approve or reject |
| POST | /api/v1/approvals/{id}/execute | Execute approved action |
| GET | /api/v1/audit | List audit logs |
| GET | /api/v1/audit/timeline/{correlation_id} | Audit timeline |
| POST | /api/v1/chat | Natural language query |
| POST | /api/v1/sync/full | Sync all source data |

## Security Model

- JWT authentication with role-based access control
- Least-privilege read-only connectors
- Deterministic policy engine (AI cannot bypass)
- All high-risk actions require explicit approval
- Simulation mode by default
- Complete audit trail with correlation IDs
- No hardcoded secrets

## Running Tests

```bash
cd apps/api
pip install -r requirements-dev.txt
pytest -v
```

## Configuration

All configuration via environment variables with `IAM_` prefix.
See `apps/api/.env.example` for the full list.

## Production Integration Points

Throughout the codebase, `TODO` markers indicate where production integrations would replace mock implementations:

- **Connectors**: Replace mock providers with real Workday API, LDAP/AD, Microsoft Graph
- **LLM Provider**: Configure OpenAI or Anthropic with real API keys
- **Action Execution**: Connect to target systems for real provisioning
- **Authentication**: Integrate with enterprise OIDC/SAML provider
- **Background Jobs**: Add Celery/Dramatiq for async sync and notifications
- **Vector Store**: Add embeddings for knowledge base retrieval
