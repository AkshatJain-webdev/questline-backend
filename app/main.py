from fastapi import FastAPI

from app.db import client, lifespan

app = FastAPI(title="Questline API", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    await client.admin.command("ping")
    return {"status": "ok", "mongo": "ok"}
