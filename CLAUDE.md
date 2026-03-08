# CLAUDE.md — Fraud Alert API & Data Platform

## Project Overview
Production-grade FastAPI service: ingest fraud alerts → PostgreSQL → Azure Data Explorer analytics.
See README.md for full spec.

## Development Workflow

### Branch Strategy
- `main` — stable, only merged via PR-style workflow
- `feature/<task-id>-<short-name>` — one branch per task (e.g., `feature/1.1-project-scaffold`)
- Always branch from `main`, always merge back to `main`
- One logical change per commit. Commit often.

### Session Handoff Protocol
Every Claude Code session MUST:
1. **On start**: Read `PROGRESS.md` to know current state
2. **On finish** (before `/clear`): Update `PROGRESS.md` with what was done and what's next

### Task Execution Flow
1. Read `PROGRESS.md` → identify current task
2. Create feature branch: `git checkout -b feature/<task-id>-<name>`
3. Implement in small, explainable steps
4. Run tests/linting after each meaningful change
5. Commit with descriptive message
6. Update `PROGRESS.md`
7. Merge to main: `git checkout main && git merge feature/<task-id>-<name>`

### Conventions
- Python 3.11+
- Formatter: black | Linter: ruff | Types: mypy
- Tests: pytest + httpx (async)
- All config via environment variables (pydantic Settings)
- Async everywhere (SQLAlchemy async, FastAPI async endpoints)

### Project Structure (target)
```
app/
  core/        # config, security, dependencies
  models/      # SQLAlchemy ORM models
  schemas/     # Pydantic request/response schemas
  routers/     # FastAPI route handlers
  services/    # Business logic layer
tests/
migrations/    # Alembic
scripts/       # seed, utilities
```

## Learning Mode
Carlos is learning alongside AI. For each task:
- Explain **why** before **how**
- Call out key concepts (e.g., "this is dependency injection")
- Flag common pitfalls
- Keep explanations brief but educational
