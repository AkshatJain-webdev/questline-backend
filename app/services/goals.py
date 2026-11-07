from typing import Any

from bson import ObjectId

from app.db import MongoDatabase
from app.models.goal import Goal
from app.models.node import Node
from app.models.prerequisite import Prerequisite
from app.services.errors import NotFoundError


async def create_goal(db: MongoDatabase, goal: Goal) -> Goal:
    return await Goal.insert(db, goal)


async def get_goal(db: MongoDatabase, goal_id: ObjectId) -> Goal:
    goal = await Goal.get(db, goal_id)
    if goal is None:
        raise NotFoundError(f"Goal {goal_id} not found")
    return goal


async def list_goals(db: MongoDatabase) -> list[Goal]:
    return await Goal.list_all(db)


async def update_goal(db: MongoDatabase, goal_id: ObjectId, changes: dict[str, Any]) -> Goal:
    current = await get_goal(db, goal_id)
    updated = Goal.model_validate(current.model_dump() | changes)
    await Goal.replace(db, updated)
    return updated


async def delete_goal(db: MongoDatabase, goal_id: ObjectId) -> None:
    await get_goal(db, goal_id)
    # Prerequisites can cross goals, so this also drops edges from other goals'
    # nodes into this one.
    node_ids = await Node.list_ids_for_goal(db, goal_id)
    await Prerequisite.delete_involving_nodes(db, node_ids)
    await Node.delete_for_goal(db, goal_id)
    await Goal.delete(db, goal_id)
