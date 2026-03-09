# Progress Tracker

## Current Status
- **Phase**: Sprint 1
- **Current Task**: 1.3 — SQLAlchemy Models + Alembic
- **Branch**: (not started)
- **State**: READY TO START

## Task Breakdown

Tasks are ordered for incremental learning. Each builds on the previous.

### Sprint 1: Core API

| ID   | Task                              | Branch                          | Status      |
|------|-----------------------------------|---------------------------------|-------------|
| 1.1  | Project scaffold + deps           | `feature/1.1-project-scaffold`  | DONE        |
| 1.2  | Pydantic config (Settings)        | `feature/1.2-pydantic-config`   | DONE        |
| 1.3  | SQLAlchemy models + Alembic       | `feature/1.3-db-models`         | NOT STARTED |
| 1.4  | Pydantic schemas (request/resp)   | `feature/1.4-schemas`           | NOT STARTED |
| 1.5  | CRUD service layer                | `feature/1.5-crud-service`      | NOT STARTED |
| 1.6  | API routers (POST/GET/PATCH)      | `feature/1.6-api-routers`       | NOT STARTED |
| 1.7  | Data generator + seed script      | `feature/1.7-data-generator`    | NOT STARTED |
| 1.8  | Makefile + pre-commit hooks       | `feature/1.8-dev-tooling`       | NOT STARTED |

### Sprint 2: Production Hardening

| ID   | Task                              | Branch                          | Status      |
|------|-----------------------------------|---------------------------------|-------------|
| 2.1  | JWT auth (token creation)         | `feature/2.1-jwt-auth`          | NOT STARTED |
| 2.2  | Role-based access control         | `feature/2.2-rbac`              | NOT STARTED |
| 2.3  | Cursor-based pagination           | `feature/2.3-pagination`        | NOT STARTED |
| 2.4  | Query filtering                   | `feature/2.4-filtering`         | NOT STARTED |
| 2.5  | Rate limiting (slowapi)           | `feature/2.5-rate-limiting`     | NOT STARTED |
| 2.6  | Error handling (RFC 7807)         | `feature/2.6-error-handling`    | NOT STARTED |
| 2.7  | Test suite (40+ tests)            | `feature/2.7-test-suite`        | NOT STARTED |
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
- **Next**: Start task 1.3 — SQLAlchemy Models + Alembic
