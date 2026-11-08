from datetime import datetime
from enum import StrEnum
from typing import Any, ClassVar, Self

from bson import ObjectId
from pydantic import Field

from app.db import MongoDatabase
from app.models.base import AppDBModel
from app.models.common import PyObjectId


class Focus(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    DEEP = "deep"


class NodeStatus(StrEnum):
    LOCKED = "locked"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ABANDONED = "abandoned"


class Node(AppDBModel):
    COLLECTION: ClassVar[str] = "nodes"

    # Human-readable id like "hld-caching-01", used in commit messages.
    slug: str
    goal_id: PyObjectId
    # Display tree only; has no effect on unlocking (that's Prerequisite).
    parent_id: PyObjectId | None = None
    title: str
    description: str
    # Output-based target the user self-reports against when ending a session.
    done_criteria: str
    # Bonus work: the parent can complete without it (no auto-created Prerequisite).
    optional: bool = False
    # What this node is worth, once done, to anything that depends on it.
    score: int = 1
    # If set, this node can only reach done once that test is passed.
    test_id: PyObjectId | None = None
    # Unlocks once the done prerequisites' scores add up to this; None = all of them.
    required_open_score: int | None = None
    est_minutes: int
    # Energy and concentration needed, combined.
    focus: Focus
    # Controlled vocabulary shared across nodes; keywords are free-form.
    tags: list[str] = Field(default_factory=list)
    # Free-form, generated when the node is created.
    keywords: list[str] = Field(default_factory=list)
    # Vector of title + description + tags, for semantic search.
    embedding: list[float] | None = None
    status: NodeStatus = NodeStatus.LOCKED
    abandon_count: int = 0
    # Links to material for working on this node.
    resources: dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime | None = None

    @classmethod
    async def list_by_ids(cls, db: MongoDatabase, node_ids: list[ObjectId]) -> list[Self]:
        cursor = db[cls.COLLECTION].find({"_id": {"$in": node_ids}})
        return [cls.model_validate(document) async for document in cursor]

    @classmethod
    async def list_for_goal(cls, db: MongoDatabase, goal_id: ObjectId) -> list[Self]:
        cursor = db[cls.COLLECTION].find({"goal_id": goal_id})
        return [cls.model_validate(document) async for document in cursor]

    @classmethod
    async def list_ids_for_goal(cls, db: MongoDatabase, goal_id: ObjectId) -> list[ObjectId]:
        return await db[cls.COLLECTION].distinct("_id", {"goal_id": goal_id})

    @classmethod
    async def has_children(cls, db: MongoDatabase, node_id: ObjectId) -> bool:
        return await db[cls.COLLECTION].find_one({"parent_id": node_id}, {"_id": 1}) is not None

    @classmethod
    async def delete_for_goal(cls, db: MongoDatabase, goal_id: ObjectId) -> None:
        await db[cls.COLLECTION].delete_many({"goal_id": goal_id})
