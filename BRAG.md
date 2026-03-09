# Brag Document — Carlos Zamora (Intern Developer)

Building a production-grade Fraud Alert API from scratch to learn backend engineering.

---

## Task 1.1 — Project Scaffolding

**What I built**: Full project scaffold — FastAPI app, dependency management, modular folder structure, first passing test.

**What I learned**:
- How Python packages work (`__init__.py` as the mechanism that makes folders importable)
- How FastAPI registers routes via decorators and serves JSON automatically
- How `APIRouter` enables modular design (separation of concerns) so large APIs stay maintainable
- Modern Python dependency management with `pyproject.toml` over legacy `requirements.txt`

**Questions I asked** (unprompted):
- "Does `__init__.py` act like an interface?" → Led to deeper understanding of Python's import system
- "How does routing work in modular designs?" → Learned APIRouter pattern before it was even scheduled (task 1.6)

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Python package structure | Solid |
| FastAPI app + decorators | Solid |
| Modular routing (APIRouter) | Solid |
| pyproject.toml + venvs | Familiar |
| async/await | Coming in 1.3 |

**Highlights**:
- Asked about scalability and modular design before being prompted — thinking ahead of the current task
- Didn't move forward until concepts clicked — prioritized understanding over speed
- Connected new ideas to existing mental models (interface analogy for packages)

---

## Task 1.2 — Pydantic Config (Settings)

**What I built**: Centralized configuration module using Pydantic `BaseSettings` that reads from environment variables, with `main.py` wired up to use it.

**What I learned**:
- How environment variables keep secrets out of code — `.env` files are gitignored, code only defines the *schema*
- The singleton pattern — one `settings` object shared across the entire app via imports
- How Pydantic `BaseSettings` auto-converts env var strings to typed Python values (str → int, bool, etc.)
- The difference between config schema (committed code) and config values (never committed)

**Questions I asked** (unprompted):
- "What about API keys? I wouldn't want them pushed to git" → Led to understanding the .env / .gitignore / env var separation
- "Would we not need to feed settings to all routes?" → Clarified that settings is a shared singleton, not passed through main.py
- Reframed config.py as "an interface between vulnerable variables and the app" — accurate mental model

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Env-driven configuration | Solid |
| Pydantic BaseSettings | Solid |
| Secret management patterns | Solid |
| Singleton pattern (module-level) | Solid |

**Highlights**:
- Proactively asked about security implications of storing API keys before being taught
- Pushed back on .env.example as unnecessary bloat — good engineering judgment about what to maintain
- Built the correct mental model independently: "config acts as an interface for vulnerable variables"

---

## Task 1.3 — SQLAlchemy Models + Alembic

**What I built**: Async database layer — engine, session factory, Base class with shared columns, Account and Alert ORM models with foreign keys and indexes, Alembic migrations that auto-generate and apply schema to PostgreSQL.

**What I learned**:
- How an ORM maps Python classes to database tables — write Python, get SQL for free
- Async engine and sessions: the server can juggle multiple requests while waiting on database I/O
- `yield` vs `return` in dependency injection — `yield` pauses so cleanup can happen after the route finishes
- Context managers (`async with`) for automatic resource cleanup (sessions, connections)
- Foreign keys enforce referential integrity — can't create an alert for a nonexistent account
- Database indexes as lookup optimization (book index analogy)
- Alembic reads model metadata, diffs it against the live DB, and generates migration scripts
- Class inheritance for shared columns (Base → Account/Alert all get id, created_at, updated_at)

**Questions I asked** (unprompted):
- "What is async_session doing with yield?" → Led to understanding generator-based dependency injection
- "What type of accounts are these?" → Clarified domain model (Azure subscription accounts being monitored)
- "Is async close to where a load balancer would be?" → Led to understanding the difference: load balancer distributes across servers, async makes a single server efficient

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| ORM model definition | Solid |
| Async engine / sessions | Familiar |
| yield-based dependencies | Familiar |
| Foreign keys + relationships | Solid |
| Database indexes | Solid |
| Alembic migrations | Familiar |
| Async vs load balancing | Familiar |

**Highlights**:
- Asked about the architectural role of async — compared it to load balancing, showing systems-level thinking
- Pushed for clarity on domain concepts (accounts) rather than blindly coding
- Requested a full code trace walkthrough to understand the flow, not just individual files

---

## Task 1.4 — Pydantic Schemas (Request/Response)

**What I built**: Pydantic schemas that define the API contract — what clients send (Create schemas) and what they receive back (Response schemas). Includes enums for validated severity levels and alert statuses.

**What I learned**:
- Why schemas and models are separate: models = database shape, schemas = API shape. Different audiences, different rules.
- `Field()` for input validation constraints (max_length, min_length) — rejects bad data before it ever touches the DB
- Enums restrict values to a fixed set — Pydantic auto-rejects invalid entries with clear error messages
- `ConfigDict(from_attributes=True)` bridges SQLAlchemy objects (attribute access) to Pydantic (dict-based by default)
- Create schemas deliberately omit DB-generated fields (id, created_at) so clients can't set them

**Questions I asked** (unprompted):
- "This is separate from the service layer correct?" → Correctly identified the boundary between data shape (schemas) and business logic (services) before being taught

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Schema vs Model separation | Solid |
| Pydantic Field validation | Solid |
| Enums for constrained values | Solid |
| from_attributes config | Familiar |
| Create vs Response patterns | Solid |

**Highlights**:
- Proactively asked about separation of concerns (schemas vs services) — architectural thinking
- Established a commit message convention `(task_id): summary` — showing ownership over project standards
- Quick to grasp the form/receipt analogy for Create vs Response schemas
