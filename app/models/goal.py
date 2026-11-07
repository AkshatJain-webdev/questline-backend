from typing import ClassVar, Self

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.db import MongoDatabase
from app.models.common import MongoDate, PyObjectId


class Goal(BaseModel):
    COLLECTION: ClassVar[str] = "goals"
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId | None = Field(default=None, alias="_id")
    title: str
    description: str
    color: str
    # Minimum minutes per week before the goal counts as neglected.
    weekly_min_minutes: int = 120
    target_date: MongoDate | None = None
    archived: bool = False

    @classmethod
    async def insert(cls, db: MongoDatabase, goal: Self) -> Self:
        # id is left out so Mongo assigns _id itself.
        result = await db[cls.COLLECTION].insert_one(goal.model_dump(exclude={"id"}))
        return goal.model_copy(update={"id": result.inserted_id})

    @classmethod
    async def replace(cls, db: MongoDatabase, goal: Self) -> None:
        await db[cls.COLLECTION].replace_one({"_id": goal.id}, goal.model_dump(exclude={"id"}))

    @classmethod
    async def get(cls, db: MongoDatabase, goal_id: ObjectId) -> Self | None:
        document = await db[cls.COLLECTION].find_one({"_id": goal_id})
        return cls.model_validate(document) if document else None

    @classmethod
    async def list_all(cls, db: MongoDatabase) -> list[Self]:
        return [cls.model_validate(document) async for document in db[cls.COLLECTION].find()]

    @classmethod
    async def delete(cls, db: MongoDatabase, goal_id: ObjectId) -> bool:
        result = await db[cls.COLLECTION].delete_one({"_id": goal_id})
        return result.deleted_count == 1
