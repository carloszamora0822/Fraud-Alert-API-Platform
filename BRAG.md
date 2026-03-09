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
