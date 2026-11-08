from fastapi import APIRouter, status
from pydantic import BaseModel

from app.models.common import MongoDate, PyObjectId
from app.models.goal import Goal
from app.services import goals
from app.services.goals import GoalTree

router = APIRouter(prefix="/goals", tags=["goals"])


class GoalCreate(BaseModel):
    title: str
    description: str
    color: str
    weekly_min_minutes: int = 120
    target_date: MongoDate | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    color: str | None = None
    weekly_min_minutes: int | None = None
    target_date: MongoDate | None = None
    archived: bool | None = None


@router.get("")
async def list_goals() -> list[Goal]:
    return await goals.list_goals()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_goal(body: GoalCreate) -> Goal:
    return await goals.create_goal(Goal.model_validate(body.model_dump()))


@router.get("/{goal_id}/tree")
async def get_goal_tree(goal_id: PyObjectId) -> GoalTree:
    return await goals.get_goal_tree(goal_id)


@router.patch("/{goal_id}")
async def update_goal(goal_id: PyObjectId, body: GoalUpdate) -> Goal:
    return await goals.update_goal(goal_id, body.model_dump(exclude_unset=True))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(goal_id: PyObjectId) -> None:
    await goals.delete_goal(goal_id)
