from bson import ObjectId

from app.db import MongoDatabase
from app.models.goal import Goal

COLLECTION = "goals"


async def insert_goal(db: MongoDatabase, goal: Goal) -> Goal:
    # id is left out so Mongo assigns _id itself.
    result = await db[COLLECTION].insert_one(goal.model_dump(exclude={"id"}))
    return goal.model_copy(update={"id": result.inserted_id})


async def get_goal(db: MongoDatabase, goal_id: ObjectId) -> Goal | None:
    document = await db[COLLECTION].find_one({"_id": goal_id})
    return Goal.model_validate(document) if document else None


async def list_goals(db: MongoDatabase) -> list[Goal]:
    return [Goal.model_validate(document) async for document in db[COLLECTION].find()]


async def replace_goal(db: MongoDatabase, goal: Goal) -> None:
    await db[COLLECTION].replace_one({"_id": goal.id}, goal.model_dump(exclude={"id"}))


async def delete_goal(db: MongoDatabase, goal_id: ObjectId) -> bool:
    result = await db[COLLECTION].delete_one({"_id": goal_id})
    return result.deleted_count == 1
