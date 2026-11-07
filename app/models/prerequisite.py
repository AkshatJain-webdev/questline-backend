from typing import ClassVar, Self

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.db import MongoDatabase
from app.models.common import PyObjectId


class Prerequisite(BaseModel):
    COLLECTION: ClassVar[str] = "prerequisites"
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId | None = Field(default=None, alias="_id")
    # prerequisite_node_id must be done before node_id can open.
    node_id: PyObjectId
    prerequisite_node_id: PyObjectId

    @classmethod
    async def insert(cls, db: MongoDatabase, prerequisite: Self) -> Self:
        # id is left out so Mongo assigns _id itself.
        result = await db[cls.COLLECTION].insert_one(prerequisite.model_dump(exclude={"id"}))
        return prerequisite.model_copy(update={"id": result.inserted_id})

    @classmethod
    async def list_all(cls, db: MongoDatabase) -> list[Self]:
        return [cls.model_validate(document) async for document in db[cls.COLLECTION].find()]

    @classmethod
    async def list_for_node(cls, db: MongoDatabase, node_id: ObjectId) -> list[Self]:
        cursor = db[cls.COLLECTION].find({"node_id": node_id})
        return [cls.model_validate(document) async for document in cursor]

    # A prerequisite is identified by its (node_id, prerequisite_node_id) pair, which
    # is unique, so callers never need to know its _id.
    @classmethod
    async def delete(
        cls, db: MongoDatabase, node_id: ObjectId, prerequisite_node_id: ObjectId
    ) -> bool:
        result = await db[cls.COLLECTION].delete_one(
            {"node_id": node_id, "prerequisite_node_id": prerequisite_node_id}
        )
        return result.deleted_count == 1

    # Removes every prerequisite with any of these nodes on either side.
    @classmethod
    async def delete_involving_nodes(cls, db: MongoDatabase, node_ids: list[ObjectId]) -> None:
        await db[cls.COLLECTION].delete_many(
            {"$or": [{"node_id": {"$in": node_ids}}, {"prerequisite_node_id": {"$in": node_ids}}]}
        )
