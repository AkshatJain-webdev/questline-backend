from bson import ObjectId

from app.db import MongoDatabase
from app.models.node import Node

COLLECTION = "nodes"


async def insert_node(db: MongoDatabase, node: Node) -> Node:
    # id is left out so Mongo assigns _id itself.
    result = await db[COLLECTION].insert_one(node.model_dump(exclude={"id"}))
    return node.model_copy(update={"id": result.inserted_id})


async def get_node(db: MongoDatabase, node_id: ObjectId) -> Node | None:
    document = await db[COLLECTION].find_one({"_id": node_id})
    return Node.model_validate(document) if document else None


async def list_nodes_for_goal(db: MongoDatabase, goal_id: ObjectId) -> list[Node]:
    cursor = db[COLLECTION].find({"goal_id": goal_id})
    return [Node.model_validate(document) async for document in cursor]


async def replace_node(db: MongoDatabase, node: Node) -> None:
    await db[COLLECTION].replace_one({"_id": node.id}, node.model_dump(exclude={"id"}))


async def delete_node(db: MongoDatabase, node_id: ObjectId) -> bool:
    result = await db[COLLECTION].delete_one({"_id": node_id})
    return result.deleted_count == 1
