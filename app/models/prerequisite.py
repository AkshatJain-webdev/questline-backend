from typing import ClassVar, Self

from bson import ObjectId

from app.db import db
from app.models.base import AppDBModel
from app.models.common import PyObjectId


class Prerequisite(AppDBModel):
    COLLECTION: ClassVar[str] = "prerequisites"

    # prerequisite_node_id must be done before node_id can open.
    node_id: PyObjectId
    prerequisite_node_id: PyObjectId

    @classmethod
    async def list_for_node(cls, node_id: ObjectId) -> list[Self]:
        cursor = db[cls.COLLECTION].find({"node_id": node_id})
        return [cls.model_validate(document) async for document in cursor]

    # Nodes that list any of these as a prerequisite.
    @classmethod
    async def list_dependent_ids(cls, prerequisite_node_ids: list[ObjectId]) -> list[ObjectId]:
        return await db[cls.COLLECTION].distinct(
            "node_id", {"prerequisite_node_id": {"$in": prerequisite_node_ids}}
        )

    @classmethod
    async def list_involving_nodes(cls, node_ids: list[ObjectId]) -> list[Self]:
        cursor = db[cls.COLLECTION].find(
            {"$or": [{"node_id": {"$in": node_ids}}, {"prerequisite_node_id": {"$in": node_ids}}]}
        )
        return [cls.model_validate(document) async for document in cursor]

    # Identified by its unique (node_id, prerequisite_node_id) pair, not its _id.
    @classmethod
    async def delete_pair(cls, node_id: ObjectId, prerequisite_node_id: ObjectId) -> bool:
        result = await db[cls.COLLECTION].delete_one(
            {"node_id": node_id, "prerequisite_node_id": prerequisite_node_id}
        )
        return result.deleted_count == 1

    # Removes every prerequisite with any of these nodes on either side.
    @classmethod
    async def delete_involving_nodes(cls, node_ids: list[ObjectId]) -> None:
        await db[cls.COLLECTION].delete_many(
            {"$or": [{"node_id": {"$in": node_ids}}, {"prerequisite_node_id": {"$in": node_ids}}]}
        )
