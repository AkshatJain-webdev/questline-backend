from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pymongo import ASCENDING, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config import settings

MongoDatabase = AsyncDatabase[dict[str, Any]]


async def create_indexes(db: MongoDatabase) -> None:
    await db["nodes"].create_index("slug", unique=True)
    await db["nodes"].create_index("goal_id")
    # Also serves lookups by node_id alone (index prefix), so node_id gets no index of its own.
    await db["prerequisites"].create_index(
        [("node_id", ASCENDING), ("prerequisite_node_id", ASCENDING)], unique=True
    )
    await db["prerequisites"].create_index("prerequisite_node_id")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    client = AsyncMongoClient(settings.mongo_uri)
    app.state.mongo_client = client
    app.state.db = client[settings.mongo_db_name]
    try:
        await create_indexes(app.state.db)
        yield
    finally:
        await client.close()
