# Fraud Alert API & Data Platform

## Objective

Design and build a production-grade RESTful API service that ingests simulated Azure fraud alerts, stores them in a relational database, integrates with Azure Data Explorer for KQL-based analytics, and serves alert data to frontend consumers with proper authentication, pagination, filtering, and error handling. This is a backend-heavy platform engineering project.

## Why This Matters at CFAR

Every tool, dashboard, and detection system at CFAR sits on top of a data platform that receives, normalizes, and serves fraud signals. Before you can build anything intelligent, you need a solid API layer that other services and frontends can consume reliably. This is the foundation layer that a SWE intern would be expected to contribute to or extend on the real team.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | Python FastAPI (async, type hints, auto-docs) |
| Database | PostgreSQL (via SQLAlchemy ORM + Alembic migrations) |
| Analytics | Azure Data Explorer (free cluster), KQL queries via SDK |
| Data Generation | Python (Faker, pydantic models) for simulated telemetry |
| Auth | JWT bearer tokens (python-jose), role-based access |
| Testing | pytest, httpx (async test client), Postman/Newman |
| Containerization | Docker, docker-compose (API + PostgreSQL + ADX connector) |
| CI/CD | Azure DevOps YAML pipeline or GitHub Actions |

## Sprint Plan

### Sprint 1 (Days 1–6)

**SWE Skills Focus:**
- FastAPI project architecture
- Pydantic schema design and validation
- SQLAlchemy ORM and Alembic migrations
- PostgreSQL indexing strategy
- RESTful API design principles

**Deliverables:**
- FastAPI project scaffolded with proper folder structure (routers, models, schemas, services, tests)
- Pydantic models defining alert schema: `alert_id`, `timestamp`, `account_id`, `resource_type`, `event_type`, `source_ip`, `geo_location`, `severity`, `raw_payload`
- Python data generator producing 10K+ realistic alerts (6 fraud types + legitimate traffic)
- PostgreSQL schema with Alembic migration: alerts table, accounts table, foreign keys, indexes on `timestamp` and `account_id`
- CRUD endpoints: `POST /alerts`, `GET /alerts`, `GET /alerts/{id}`, `PATCH /alerts/{id}/status`

**Definition of Done:** API accepts POST requests, persists alerts to PostgreSQL, and returns paginated results on GET. All schemas validated. Migrations run cleanly.

### Sprint 2 (Days 7–12)

**SWE Skills Focus:**
- JWT auth implementation
- Cursor-based pagination patterns
- API error handling and status codes
- Rate limiting design
- Integration testing with httpx

**Deliverables:**
- JWT authentication middleware with role-based access (analyst, admin, service)
- Query filtering: by date range, severity, fraud type, account_id, geo_location
- Cursor-based pagination (not offset) for large result sets
- Rate limiting middleware (slowapi)
- Structured error responses (RFC 7807 Problem Details format)
- Comprehensive test suite: 40+ tests covering auth, CRUD, filtering, pagination, edge cases
- Postman collection with environment variables and test assertions

**Definition of Done:** API is production-quality: authenticated, paginated, filtered, rate-limited, with proper error responses. Test suite passes with 90%+ coverage.

### Sprint 3 (Days 13–18)

**SWE Skills Focus:**
- Azure Data Explorer SDK integration
- KQL query authoring
- Docker Compose multi-service orchestration
- CI/CD pipeline authoring (YAML)
- API documentation best practices

**Deliverables:**
- Azure Data Explorer integration: alerts replicated to ADX for KQL analytics
- KQL query service: 8+ pre-built detection queries exposed via `/analytics` endpoints
- Analytics endpoints: `GET /analytics/provisioning-spikes`, `/analytics/auth-anomalies`, `/analytics/geo-outliers`, `/analytics/billing-surges`
- Docker Compose: API + PostgreSQL + test runner
- CI/CD pipeline: lint (ruff), test, build image, push to registry
- OpenAPI spec auto-generated and verified
- README with architecture diagram, setup instructions, API examples

**Definition of Done:** Full platform running in containers. KQL analytics endpoints return results. CI/CD pipeline builds and tests on every push. API docs are complete.

## User Stories & Subtasks

### P1-01: Project Scaffolding

> As a backend engineer, I need a well-structured FastAPI project so the codebase is maintainable and testable from day one.

**Stack:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, ruff, black, mypy

**Subtasks:**
1. Scaffold project: `/app` (routers/, models/, schemas/, services/, core/), `/tests`, `/migrations`, `/scripts`
2. Configure pydantic Settings for env-based config (`DB_URL`, `JWT_SECRET`, `ADX_CLUSTER`)
3. Set up SQLAlchemy async engine with connection pooling
4. Create Alembic config and initial migration with alerts + accounts tables
5. Add pre-commit hooks: ruff linter, black formatter, mypy type checking
6. Write Makefile with targets: `dev`, `test`, `lint`, `migrate`, `seed`

### P1-02: Realistic Alert Data Feed

> As a platform consumer, I need a realistic alert data feed so I can develop and test against data that mirrors real Azure telemetry.

**Stack:** Python, Faker, pydantic

**Subtasks:**
1. Define pydantic `AlertCreate` schema matching Azure Resource Manager event structure
2. Build generator with Faker: account creation, VM provisioning, auth success/failure, quota change, billing events
3. Inject fraud patterns: burst provisioning (50+ VMs in 5 min), impossible travel (2 logins 5000km apart in 10 min), billing spikes (10x baseline), suspicious API calls
4. Include 70% legitimate traffic with realistic noise
5. Write seed command: `python -m scripts.seed --count 10000`
6. Validate output with schema assertions

### P1-03: CRUD Endpoints

> As a frontend developer, I need reliable CRUD endpoints with proper pagination and filtering so I can build UIs against a stable contract.

**Stack:** FastAPI, SQLAlchemy, pydantic, httpx

**Subtasks:**
1. `POST /alerts`: validate with pydantic, persist to DB, return 201 with created resource
2. `GET /alerts`: cursor-based pagination (`after_id` + `limit`), sort by timestamp desc
3. Add query params: `severity`, `fraud_type`, `account_id`, `start_date`, `end_date`, `geo_location`
4. `GET /alerts/{id}`: return single alert with full payload, 404 if not found
5. `PATCH /alerts/{id}/status`: update investigation status (`new`/`investigating`/`resolved`/`dismissed`)
6. Return `Link` headers for pagination, `X-Total-Count` header

### P1-04: Authentication & Rate Limiting

> As a security engineer, I need the API authenticated and rate-limited so only authorized services and analysts can access alert data.

**Stack:** python-jose, passlib, slowapi, pytest

**Subtasks:**
1. Implement JWT token creation (`POST /auth/token`) with username/password + role claim
2. Add `Depends(get_current_user)` middleware to all protected routes
3. Implement role-based access: analysts read-only, admins full CRUD, service accounts POST-only
4. Add rate limiting with slowapi: 100 req/min for analysts, 1000 req/min for service accounts
5. Return 401 (no token), 403 (wrong role), 429 (rate limited) with RFC 7807 bodies
6. Write tests for each auth scenario including expired tokens and malformed headers

### P1-05: KQL Analytics Endpoints

> As a security analyst, I need KQL-powered analytics endpoints so I can query fraud patterns without writing raw queries.

**Stack:** Azure Data Explorer, azure-kusto-data SDK, KQL

**Subtasks:**
1. Set up Azure Data Explorer free cluster and create alerts table with schema
2. Build data sync service: batch insert new alerts from PostgreSQL to ADX every 5 minutes
3. Write KQL detection queries: provisioning velocity spikes, auth failure clustering, geo anomaly detection, billing surge detection, quota abuse patterns, temporal pattern analysis, cross-account correlation, new account risk scoring
4. Expose as `GET /analytics/{query_name}` with date range params
5. Return structured JSON with results + query metadata (execution time, row count)

### P1-06: Containerization & CI/CD

> As a DevOps engineer, I need the entire platform containerized with CI/CD so it deploys reliably across environments.

**Stack:** Docker, docker-compose, Azure DevOps / GitHub Actions, YAML

**Subtasks:**
1. Write Dockerfile: multi-stage build (builder with deps, runtime with slim image)
2. Write `docker-compose.yml`: api (FastAPI), db (PostgreSQL), test-runner
3. Add healthcheck endpoints: `GET /health` (API), `GET /health/db` (database connectivity)
4. Write YAML pipeline: install deps, lint (ruff), test (pytest with coverage), build image, push to registry
5. Add pipeline gate: fail if test coverage drops below 80%
6. Write README: architecture diagram (Mermaid), local setup, API usage examples with curl

## Key Deliverables

- Production-grade FastAPI service with JWT auth, pagination, filtering, rate limiting
- PostgreSQL database with Alembic migrations and proper indexing
- Data generator producing 10K+ realistic fraud alerts
- 8 KQL analytics endpoints powered by Azure Data Explorer
- 40+ integration tests with 90%+ coverage
- Docker Compose deployment with CI/CD pipeline
- Complete API documentation (auto-generated OpenAPI + README)
