from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pymongo import ASCENDING, AsyncMongoClient

from app.config import settings

# One client per process: it's a connection pool, and creating it doesn't connect yet.
client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]


async def create_indexes() -> None:
    await db["nodes"].create_index("slug", unique=True)
    await db["nodes"].create_index("goal_id")
    # Also serves lookups by node_id alone (index prefix), so node_id gets no index of its own.
    await db["prerequisites"].create_index(
        [("node_id", ASCENDING), ("prerequisite_node_id", ASCENDING)], unique=True
    )
    await db["prerequisites"].create_index("prerequisite_node_id")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    try:
        await create_indexes()
        yield
    finally:
        await client.close()
