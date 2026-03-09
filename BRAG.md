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
