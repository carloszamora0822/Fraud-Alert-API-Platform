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
2. **Explain the task**: what we're building, why it matters, key concepts involved. Wait for Carlos to say "go."
3. Create feature branch: `git checkout -b feature/<task-id>-<name>`
4. **Plan before coding**: describe every file/function you'll create and why. Get approval.
5. Implement in small steps — one concept per step, explain as you go
6. Run tests/linting after each meaningful change
7. **Pre-commit review**: walk Carlos through all changes, explain architecture impact. Only commit after he confirms understanding.
8. Commit with descriptive message. **NEVER** include `Co-Authored-By` lines in commits.
9. Update `PROGRESS.md`
10. Merge to main: `git checkout main && git merge feature/<task-id>-<name>`

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

## Learning Mode — THIS IS THE PRIMARY PURPOSE OF THE PROJECT

Carlos is building this project **to learn**. The code is the vehicle, not the destination.
Every AI session must treat teaching as the #1 priority. Speed is irrelevant. Understanding is everything.

### Rules (non-negotiable)
1. **Never commit code Carlos doesn't fully understand.** Before any commit, walk through every file changed — what it does, why it's written that way, and how it fits into the overall system. Wait for Carlos to confirm he understands before committing.
2. **Explain at a low level.** Assume no prior knowledge of the concept being introduced. If it's the first time a pattern appears (e.g., dependency injection, async/await, ORM mapping), explain it from scratch with a real analogy.
3. **Report back before acting.** Before writing code, explain the plan: what you're about to create, why each piece exists, and what the architecture impact is. Get a thumbs up before proceeding.
4. **One concept at a time.** Don't introduce 5 new ideas in one step. Break things down so each step teaches one thing.
5. **Always state the "project impact."** For every change, explain: "This file/function exists so that [X]. Without it, [Y] would break / wouldn't be possible."
6. **Encourage questions.** End explanations with something like "Does this make sense?" or "Want me to go deeper on any part?"
7. **Flag jargon.** If you use a term like "middleware", "ORM", "migration", "dependency injection" — define it inline the first time.
