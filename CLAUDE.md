# Questline Backend

FastAPI + MongoDB backend for Questline, a personal goal tracker built as skill trees.

## Architecture rules

- **Routers (`app/api/`) handle HTTP only** — request parsing, response shaping, status codes. No business logic.
- **Business logic lives in `app/services/`.** Routers, the MCP server (`app/mcp/`, from M4) and scheduled jobs all call services — never the DB directly.
- **`app/algorithms/` is pure.** No DB access, no I/O. Picker, bandit, forecast, calibration, unlock, readiness — all plain functions, with any randomness passed in via an `rng` parameter so results are reproducible.
- **Validation is Pydantic v2 models in `app/models/`.** No Mongo-level `$jsonSchema` validators.
- **LLM output (from M5 onward) is always schema-validated** before it touches the DB.

## Working style

- One milestone at a time, scoped by its own `TASK.md` before implementation starts.
- Each implementation slice is one commit, and the app runs at every commit.
- **No tests.** Don't write tests or add test tooling (pytest, test clients, fixtures) to this repo. Verify changes by running the app and exercising it directly.
