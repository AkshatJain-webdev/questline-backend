import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = AsyncMongoClient(MONGO_URI)
    app.state.mongo_client = client
    try:
        yield
    finally:
        await client.close()
