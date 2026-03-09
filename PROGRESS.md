# Progress Tracker

## Current Status
- **Phase**: Sprint 1
- **Current Task**: 2.8 — Postman Collection
- **Branch**: (not started)
- **State**: READY TO START

## Task Breakdown

Tasks are ordered for incremental learning. Each builds on the previous.

### Sprint 1: Core API

| ID   | Task                              | Branch                          | Status      |
|------|-----------------------------------|---------------------------------|-------------|
| 1.1  | Project scaffold + deps           | `feature/1.1-project-scaffold`  | DONE        |
| 1.2  | Pydantic config (Settings)        | `feature/1.2-pydantic-config`   | DONE        |
| 1.3  | SQLAlchemy models + Alembic       | `feature/1.3-db-models`         | DONE        |
| 1.4  | Pydantic schemas (request/resp)   | `feature/1.4-schemas`           | DONE        |
| 1.5  | CRUD service layer                | `feature/1.5-crud-service`      | DONE        |
| 1.6  | API routers (POST/GET/PATCH)      | `feature/1.6-api-routers`       | DONE        |
| 1.7  | Data generator + seed script      | `feature/1.7-data-generator`    | DONE        |
| 1.8  | Makefile + pre-commit hooks       | `feature/1.8-dev-tooling`       | DONE        |

### Sprint 2: Production Hardening

| ID   | Task                              | Branch                          | Status      |
|------|-----------------------------------|---------------------------------|-------------|
| 2.1  | JWT auth (token creation)         | `feature/2.1-jwt-auth`          | DONE        |
| 2.2  | Role-based access control         | `feature/2.2-rbac`              | DONE        |
| 2.3  | Cursor-based pagination           | `feature/2.3-pagination`        | DONE        |
| 2.4  | Query filtering                   | `feature/2.4-filtering`         | DONE        |
| 2.5  | Rate limiting (slowapi)           | `feature/2.5-rate-limiting`     | DONE        |
| 2.6  | Error handling (RFC 7807)         | `feature/2.6-error-handling`    | DONE        |
| 2.7  | Test suite (40+ tests)            | `feature/2.7-test-suite`        | DONE        |
| 2.8  | Postman collection                | `feature/2.8-postman`           | NOT STARTED |

### Sprint 3: Analytics & DevOps

| ID   | Task                              | Branch                          | Status      |
|------|-----------------------------------|---------------------------------|-------------|
| 3.1  | ADX cluster setup + table         | `feature/3.1-adx-setup`        | NOT STARTED |
| 3.2  | Data sync service (PG → ADX)     | `feature/3.2-data-sync`         | NOT STARTED |
| 3.3  | KQL detection queries             | `feature/3.3-kql-queries`       | NOT STARTED |
| 3.4  | Analytics API endpoints           | `feature/3.4-analytics-api`     | NOT STARTED |
| 3.5  | Dockerfile (multi-stage)          | `feature/3.5-dockerfile`        | NOT STARTED |
| 3.6  | Docker Compose                    | `feature/3.6-docker-compose`    | NOT STARTED |
| 3.7  | Health check endpoints            | `feature/3.7-health-checks`     | NOT STARTED |
| 3.8  | CI/CD pipeline                    | `feature/3.8-ci-cd`             | NOT STARTED |

## Session Log

### Session 1 — 2026-03-09
- Created execution framework (CLAUDE.md, PROGRESS.md)
- Initialized git repo on `main`
- **Next**: Start task 1.1 — Project Scaffolding
- Completed task 1.1: scaffold, pyproject.toml, /health endpoint, test passing
- Completed task 1.2: Pydantic Settings config module, updated main.py to use settings
- Completed task 1.3: async database engine, Account + Alert ORM models, Alembic migration applied
- Completed task 1.4: Pydantic schemas (AccountCreate/Response, AlertCreate/Response/StatusUpdate, enums)
- Completed task 1.5: CRUD service layer — account (create, get, list) and alert (create, get, list, update_status)
- Completed task 1.6: API routers for accounts (3 endpoints) and alerts (4 endpoints) under /api/v1
- Completed task 1.7: Faker-based data generator (scripts/generate.py) + seed script (scripts/seed.py) — 20 accounts, 10K alerts, 6 fraud types + legitimate traffic
- Completed task 1.8: Makefile (9 targets), pre-commit hooks (black + ruff), fixed mypy type errors
- **Sprint 1 COMPLETE** — Next: Start Sprint 2, task 2.1 — JWT Auth

### Session 2 — 2026-03-09
- Completed task 2.1: JWT auth — User model, bcrypt password hashing, register/login endpoints, get_current_user dependency, Alembic migration
- **Next**: Start task 2.2 — Role-Based Access Control
- Completed task 2.2: RBAC — role hierarchy, require_role dependency factory, protected all routes (analyst=read, admin=write)
- Completed task 2.3: Cursor-based pagination — PaginatedResponse schema, encode/decode cursor helpers, limit+1 trick, tuple_ tiebreaker
- Completed task 2.4: Query filtering — AlertFilters schema, dynamic WHERE clauses, Depends() injection
- **Next**: Start task 2.5 — Rate Limiting
- Completed task 2.5: Role-based rate limiting with slowapi — 100/min analyst, 1000/min admin, 20/min auth endpoints, in-memory storage
- **Next**: Start task 2.6 — Error Handling (RFC 7807)
- Completed task 2.6: RFC 7807 error handling — custom exception classes, global handlers, consistent problem+json responses across all endpoints
- **Next**: Start task 2.7 — Test Suite
- Completed task 2.7: 43-test suite — conftest with savepoint rollback, tests for auth, accounts, alerts, error handling, RBAC, health. Fixed alert_id→account_id bug in accounts router.
- **Next**: Start task 2.8 — Postman Collection
