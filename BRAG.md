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

---

## Task 1.5 — CRUD Service Layer

**What I built**: Service layer with async functions for Account CRUD (create, get, list) and Alert CRUD (create, get, list with optional filtering, status updates). This is the business logic layer that sits between API routes and the database.

**What I learned**:
- The service layer pattern — separating "what to do" (service) from "how to receive requests" (routes) and "how data is stored" (ORM)
- How `select().where()` builds SQL queries as Python objects — composable and conditional
- The commit/refresh dance: `db.add()` stages, `db.commit()` sends to DB, `db.refresh()` pulls back DB-generated values
- The session is the messenger that actually talks to PostgreSQL, using the ORM as a map
- Tracked objects: once you fetch an ORM object, the session watches it — changing an attribute and committing generates an UPDATE automatically

**Questions I asked** (unprompted):
- "Where does the actual filtering/searching come into play?" → Led to understanding `select().where()` as the filtering mechanism
- "Explain the role of account service in relation to schema and ORM" → Built a clear mental model of the full chain: Schema validates → Service orchestrates → Session sends → ORM maps → PostgreSQL stores
- "Would refresh not be ineffective with multiple transactions?" → Showed understanding of concurrency concerns; led to learning about transaction isolation and per-request sessions

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Service layer pattern | Solid |
| SQLAlchemy select/where | Solid |
| commit/refresh pattern | Solid |
| Schema → Service → ORM → DB flow | Solid |
| Transaction isolation basics | Familiar |

**Highlights**:
- Independently questioned concurrency implications of `refresh()` — production-level thinking
- Asked about the full architectural chain (schema, service, ORM, DB) and synthesized it into a clear mental model
- Distinguished between ORM (the map) and session (the messenger) — a nuance many beginners miss

---

## Task 1.6 — API Routers

**What I built**: FastAPI route handlers for accounts (POST/GET/GET-by-ID) and alerts (POST/GET/GET-by-ID/PATCH-status), wired into the app under `/api/v1`. This is the front door — the layer that receives HTTP requests and connects them to the service layer.

**What I learned**:
- Routers are thin wrappers — they receive requests, delegate to services, and return responses. Almost no logic lives here.
- `Depends(get_db)` is dependency injection: FastAPI calls `get_db()` automatically and hands the session to the route. Only routers use `Depends` — services just receive `db` as a normal argument.
- `HTTPException(status_code=404)` is how you return error responses — FastAPI converts it to a proper JSON error.
- `include_router()` with prefix stacking: router defines `/accounts`, `include_router` adds `/api/v1`, final path is `/api/v1/accounts`.
- `Query(default=None)` makes a parameter optional in the URL query string (e.g., `/alerts?account_id=...`).

**Questions I asked** (unprompted):
- "There's so many layers — what happens when I create a user?" → Traced the full request lifecycle: Client → Router → Schema validates → Service → ORM → DB → Response. Built a complete mental model of the entire stack.
- "Why do we call db in so many spots?" → Led to understanding that `db` is passed like a baton — created once in the router via `Depends`, then handed down. Services are "dumb" about where it came from.
- "We only ever use get_db in the router layer then?" → Correctly identified that `Depends` is router-only; downstream layers just receive `db` as a plain argument.

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Router as thin wiring layer | Solid |
| Dependency injection (Depends) | Solid |
| HTTPException for errors | Solid |
| Prefix stacking (include_router) | Solid |
| Full request lifecycle (Client → Router → Schema → Service → ORM → DB) | Solid |

**Highlights**:
- Asked to trace a full request end-to-end — wanted to understand how all 5 layers connect, not just the current one
- Independently realized that `get_db` is only used at the router level — grasped the architectural boundary between DI and plain arguments
- Questioned why `db` appears in so many places — didn't accept repetition without understanding the reason

---

## Task 1.7 — Data Generator + Seed Script

**What I built**: Faker-based data generator (`scripts/generate.py`) producing 20 accounts and 10K+ realistic fraud alerts across 6 fraud types + legitimate traffic, plus a seed script (`scripts/seed.py`) that inserts everything into PostgreSQL by reusing the existing CRUD service layer.

**What I learned**:
- The difference between fraud *detection* (upstream systems like Azure Sentinel) and fraud *analytics* (our platform) — we store and serve already-classified alerts, we don't build the detection algorithms
- 6 fraud types in depth: impossible_travel, brute_force, privilege_escalation, data_exfiltration, suspicious_login, resource_abuse — what each means, why CFAR cares, and real-world implications
- Modern frontier fraud: deepfake identity fraud, synthetic identities, prompt injection attacks, account farming, real-time payment fraud
- Batch seeding (instant, fake timestamps) vs real-time ingestion (continuous stream) — seed data is for development, real systems receive alerts 24/7
- The service layer is reusable — the seed script calls the same `create_account`/`create_alert` functions as the API routes, proving the abstraction works
- Public vs private functions: prefix with `_` to signal "implementation detail, don't call this directly"

**Questions I asked** (unprompted):
- "Do I have to create the policies/business logic for the 6 fraud types?" → Showed he was thinking about system boundaries — where does detection end and our platform begin?
- "Would alerts come in real-time or automatically populate?" → Led to understanding batch vs streaming data ingestion patterns
- Asked about modern fraud types beyond the 6 — curious about the industry frontier, not just the project scope

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Detection vs analytics platform distinction | Solid |
| Fraud type taxonomy (6 types) | Solid |
| Service layer reusability | Solid |
| Batch seeding vs real-time ingestion | Solid |
| Weighted random distributions | Familiar |

**Highlights**:
- Questioned the system boundary between detection and analytics — architectural thinking about what's in scope vs out of scope
- Proactively asked about industry-frontier fraud types — intellectual curiosity beyond the assignment
- Understood the data flow diagram (Generator → Service → ORM → DB) and how it mirrors the API flow (Router → Service → ORM → DB) — grasped that both converge at the service layer

---

## Task 1.8 — Makefile + Pre-commit Hooks

**What I built**: Developer tooling — a Makefile with 9 shortcut targets (dev, test, format, lint, typecheck, check, migrate, seed, install) and pre-commit hooks that auto-run black + ruff on every git commit. Also fixed all mypy type errors across the codebase.

**What I learned**:
- Makefiles aren't just for compiling — they're command menus. Any project can use them as shortcut runners for common tasks.
- Pre-commit hooks are git's built-in automation: scripts that run before each commit. The `pre-commit` framework manages them via a YAML config file.
- The three layers of quality enforcement: Makefile (manual), pre-commit (automatic on commit), CI/CD pipeline (automatic on push) — and how CI often calls Makefile targets for a single source of truth.
- `TYPE_CHECKING` pattern: import types only during static analysis to avoid circular imports at runtime — needed when two models reference each other.
- `from __future__ import annotations` makes all type hints strings by default, deferring evaluation.

**Questions I asked** (unprompted):
- "How is a Makefile different from the YAML file?" → Distinguished between a command runner (Makefile) and a config file (YAML). Corrected the misconception that Makefiles are only for compiling.
- "Would a deployment pipeline YAML use the Makefile commands?" → Connected the dots between local tooling and CI/CD — understood the single-source-of-truth pattern before being taught it.

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Makefile as command runner | Solid |
| Pre-commit hooks | Solid |
| Local vs CI quality enforcement | Solid |
| TYPE_CHECKING for circular imports | Familiar |
| Three-layer quality enforcement | Solid |

**Highlights**:
- Proactively asked how Makefiles connect to CI/CD pipelines — systems thinking about how tools compose across environments
- Correctly intuited that pipeline YAML would call Makefile targets — understood DRY principle applied to DevOps
- Sprint 1 complete: 8 tasks, full API from scaffold to dev tooling

---

## Task 2.1 — JWT Authentication

**What I built**: Full JWT auth system — User model with bcrypt password hashing, register and login endpoints, a `get_current_user` dependency that decodes and validates tokens on protected routes, and an Alembic migration for the `users` table.

**What I learned**:
- The complete JWT workflow: register (hash + store) → login (verify + issue token) → protected request (decode + validate)
- How bcrypt works: one-way hashing with a random salt embedded in the output. Same password + same salt = same hash, but the salt is only generated once at registration
- Why salts exist: they defeat rainbow table attacks by making identical passwords produce different hashes per user
- JWT structure: header.payload.signature — the payload is readable by anyone (base64), but the signature prevents tampering
- The difference between hashing (one-way, irreversible) and encryption (two-way, reversible) — passwords use hashing because you never need the original back
- How `OAuth2PasswordBearer` works as a FastAPI helper that extracts tokens from the Authorization header
- Short-lived tokens as a security boundary — 30 min expiry limits damage if a token is stolen

**Questions I asked** (unprompted):
- "The salt... it doesn't make sense how I can have the same password but different results" → Pushed until he understood that the salt is stored inside the hash and reused on login
- "Couldn't they just find the password in that message?" → Led to understanding one-way hashing — you can't reverse a hash, the salt isn't a decryption key
- "Does salt provide instructions on how to decrypt?" → Refined understanding: salt changes the hashing recipe (like a spice), it doesn't enable decryption
- "When we relogin, how do we know whether that is right or wrong compared to the stored hash?" → Traced the full verify flow: extract salt from stored hash → re-hash input with same salt → compare

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| JWT workflow (register → login → validate) | Solid |
| Bcrypt hashing + salt | Solid |
| One-way hashing vs encryption | Solid |
| Rainbow table attacks + salt defense | Solid |
| FastAPI dependency for auth | Solid |
| Token expiry as security measure | Solid |

**Highlights**:
- Didn't accept "bcrypt uses a salt" at face value — asked 4 follow-up questions until the full mechanism clicked
- Distinguished between hashing and encryption unprompted — asked "couldn't they find the password in the hash?" which shows he was testing his own assumptions
- Asked about the security approach holistically ("which is of most security?") before diving into implementation — security-first thinking

---

## Task 2.2 — Role-Based Access Control (RBAC)

**What I built**: A role hierarchy system (analyst < admin < superadmin) with a `require_role()` dependency factory that protects every API endpoint. GET routes require analyst, POST/PATCH require admin.

**What I learned**:
- The difference between authentication (who are you?) and authorization (what can you do?)
- How closures work — a function that "remembers" variables from when it was created
- Dependency factories — functions that return dependencies, allowing parameterized access control
- HTTP 401 vs 403 — unauthorized (bad identity) vs forbidden (insufficient permissions)
- The `_variable` convention in Python for "needed but unused" parameters

**Questions I asked** (unprompted):
- Asked for a data flow summary to understand how the pieces connect — shows preference for visual/sequential reasoning over abstract explanations
- Admitted conceptual understanding was solid but code readability was the gap — self-aware about where to focus learning

**Concept Mastery**:
| Concept | Confidence |
|---|---|
| Auth vs authorization (401 vs 403) | Solid |
| Role hierarchy as list index comparison | Solid |
| Closures / dependency factories | Conceptual (needs more practice reading the syntax) |
| Depends() chaining in FastAPI | Conceptual |

**Highlights**:
- Honest about his learning edge — said "conceptually I get it, in practice I struggle to read the code" — this kind of self-assessment is rare and valuable for growth
- Asked for a data flow diagram rather than just accepting the explanation — shows he's optimizing for real understanding, not just moving forward
