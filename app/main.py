from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import goals, nodes, prerequisites
from app.config import settings
from app.db import client, lifespan
from app.services.errors import AppError, handle_app_error

app = FastAPI(title="Questline API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(goals.router, prefix="/api")
app.include_router(nodes.router, prefix="/api")
app.include_router(prerequisites.router, prefix="/api")
# Starlette types every handler as taking Exception, though this one only ever gets an AppError.
app.add_exception_handler(AppError, handle_app_error)  # type: ignore[arg-type]


@app.get("/health")
async def health() -> dict[str, str]:
    await client.admin.command("ping")
    return {"status": "ok", "mongo": "ok"}
