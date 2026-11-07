from bson import ObjectId

from app.db import MongoDatabase
from app.models.prerequisite import Prerequisite

COLLECTION = "prerequisites"


async def insert_prerequisite(db: MongoDatabase, prerequisite: Prerequisite) -> Prerequisite:
    # id is left out so Mongo assigns _id itself.
    result = await db[COLLECTION].insert_one(prerequisite.model_dump(exclude={"id"}))
    return prerequisite.model_copy(update={"id": result.inserted_id})


async def list_prerequisites_for_node(
    db: MongoDatabase, node_id: ObjectId
) -> list[Prerequisite]:
    cursor = db[COLLECTION].find({"node_id": node_id})
    return [Prerequisite.model_validate(document) async for document in cursor]


# A prerequisite is identified by its (node_id, prerequisite_node_id) pair, which
# is unique, so callers never need to know its _id.
async def delete_prerequisite(
    db: MongoDatabase, node_id: ObjectId, prerequisite_node_id: ObjectId
) -> bool:
    result = await db[COLLECTION].delete_one(
        {"node_id": node_id, "prerequisite_node_id": prerequisite_node_id}
    )
    return result.deleted_count == 1
