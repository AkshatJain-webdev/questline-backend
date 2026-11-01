from fastapi import FastAPI, Request

from app.db import lifespan

app = FastAPI(title="Questline API", lifespan=lifespan)


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    await request.app.state.mongo_client.admin.command("ping")
    return {"status": "ok", "mongo": "ok"}
