# Questline Backend

FastAPI and MongoDB API for Questline, a personal goal tracker built as skill trees. The web app lives in [questline-frontend](https://github.com/AkshatJain-webdev/questline-frontend).

## Getting started

You need [uv](https://docs.astral.sh/uv/) and MongoDB running on port 27017.

```bash
uv venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
uv sync --dev
uvicorn app.main:app --reload
```

The API runs at <http://localhost:8000>, with interactive docs at <http://localhost:8000/docs>.

## Seed the database

Load the starter roadmap once, against an empty database:

```bash
python -m scripts.seed
```

## Docker

```bash
docker compose up --build
docker compose run --rm backend python -m scripts.seed
```

## Configuration

Set these in the environment or in a git-ignored `.env` file. All of them have local defaults.

| Variable | Default | Purpose |
| --- | --- | --- |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `questline` | Database name |
| `CORS_ALLOWED_ORIGINS` | `["http://localhost:3000"]` | Web app origins allowed to call the API, as a JSON list |
