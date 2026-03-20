# Local Development Setup

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (via Docker)

## Quick Start with Docker Compose

```bash
# Start all services
docker compose up -d

# Wait for services to be healthy
docker compose ps

# Seed mock data
python scripts/seed.py

# Open the UI
open http://localhost:3000
```

## Manual Setup (without Docker)

### 1. Database

```bash
# Start PostgreSQL
docker run -d --name iam-db \
  -e POSTGRES_DB=agentic_iam \
  -e POSTGRES_USER=iam_user \
  -e POSTGRES_PASSWORD=iam_pass \
  -p 5432:5432 \
  postgres:16-alpine

# Start Redis
docker run -d --name iam-redis -p 6379:6379 redis:7-alpine
```

### 2. Backend API

```bash
cd apps/api

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure env
cp .env.example .env

# Run the API
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd apps/web

# Install dependencies
npm install

# Run the dev server
npm run dev
```

### 4. Seed Data

```bash
# Install httpx for the seed script
pip install httpx

# Run seed
python scripts/seed.py
```

## Environment Variables

See `apps/api/.env.example` for all configuration options.

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| IAM_ENVIRONMENT | local | Environment name |
| IAM_DATABASE_URL | postgresql+asyncpg://... | Database connection |
| IAM_LLM_PROVIDER | mock | LLM provider (mock/openai/anthropic) |
| IAM_ACTION_MODE | simulation | Action execution mode |
| IAM_CONNECTOR_MODE | mock | Source connector mode |

## Running Tests

```bash
cd apps/api
pip install -r requirements-dev.txt
pytest -v
```

## API Documentation

When the API is running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json
