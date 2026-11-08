from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ValidationError

from app.models.goal import Goal
from app.models.node import Node
from app.models.prerequisite import Prerequisite
from app.services.errors import InvalidError, NotFoundError
from app.services.lifecycle import recompute_statuses


async def create_goal(goal: Goal) -> Goal:
    return await Goal.insert(goal)


async def get_goal(goal_id: ObjectId) -> Goal:
    goal = await Goal.get(goal_id)
    if goal is None:
        raise NotFoundError(f"Goal {goal_id} not found")
    return goal


async def list_goals() -> list[Goal]:
    return await Goal.list_all()


class GoalTree(BaseModel):
    goal: Goal
    nodes: list[Node]
    # Includes edges to or from other goals' nodes.
    prerequisites: list[Prerequisite]


async def get_goal_tree(goal_id: ObjectId) -> GoalTree:
    goal = await get_goal(goal_id)
    nodes = await Node.list_for_goal(goal_id)
    prerequisites = await Prerequisite.list_involving_nodes([node.id for node in nodes])
    return GoalTree(goal=goal, nodes=nodes, prerequisites=prerequisites)


async def update_goal(goal_id: ObjectId, changes: dict[str, Any]) -> Goal:
    current = await get_goal(goal_id)
    try:
        updated = Goal.model_validate(current.model_dump() | changes)
    except ValidationError as error:
        raise InvalidError.from_validation_error(error) from None
    await Goal.replace(updated)
    return updated


async def delete_goal(goal_id: ObjectId) -> None:
    await get_goal(goal_id)
    node_ids = await Node.list_ids_for_goal(goal_id)
    # Prerequisites can cross goals, so nodes elsewhere may unlock once these are gone.
    dependent_ids = await Prerequisite.list_dependent_ids(node_ids)
    await Prerequisite.delete_involving_nodes(node_ids)
    await Node.delete_for_goal(goal_id)
    await Goal.delete(goal_id)
    await recompute_statuses(dependent_ids)
