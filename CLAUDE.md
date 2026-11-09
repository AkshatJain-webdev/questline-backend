# Questline Backend

FastAPI + MongoDB backend for Questline, a personal goal tracker built as skill trees.

## Architecture rules

- **Routers (`app/api/`) handle HTTP only** — request parsing, response shaping, status codes. No business logic.
- **Business logic lives in `app/services/`.** Routers, the MCP server (`app/mcp/`, from M5) and scheduled jobs all call services — never the DB directly.
- **`app/algorithms/` is pure.** No DB access, no I/O. Picker, bandit, forecast, calibration, unlock, readiness — all plain functions, with any randomness passed in via an `rng` parameter so results are reproducible.
- **Validation is Pydantic v2 models in `app/models/`.** No Mongo-level `$jsonSchema` validators.
- **Each model owns its queries.** All database access goes through classmethods on the model classes (`Node.get(id)`, `Node.insert(node)`, `Prerequisite.delete_involving_nodes(ids)`, …), which use the single module-level `db` from `app/db.py`. Services and routers never call `db[collection]` directly; a new query means a new method on the model.
- **LLM output (from M6 onward) is always schema-validated** before it touches the DB.
- **All configuration lives in `app/config.py`.** Each environment variable is a typed field on `Settings` (with a default when a safe local one exists), and code reads it via `from app.config import settings`. Never call `os.environ` / `os.getenv` anywhere else. A new variable means a new field there, never a direct env lookup at the call site. Local overrides go in a git-ignored `.env` at the repo root.

## Working style

- One milestone at a time, scoped by its own `TASK.md` before implementation starts.
- Each implementation slice is one commit, and the app runs at every commit.
- **No tests.** Don't write tests or add test tooling (pytest, test clients, fixtures) to this repo. Verify changes by running the app and exercising it directly.
