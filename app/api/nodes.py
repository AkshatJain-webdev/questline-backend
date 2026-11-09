from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.models.common import PyObjectId
from app.models.node import Focus, Node
from app.services import nodes

router = APIRouter(prefix="/nodes", tags=["nodes"])


# Status, keywords and embedding are set by the server, never by the client.
class NodeCreate(BaseModel):
    slug: str
    goal_id: PyObjectId
    parent_id: PyObjectId | None = None
    title: str
    description: str
    done_criteria: str
    optional: bool = False
    score: int = 1
    test_id: PyObjectId | None = None
    required_open_score: int | None = None
    est_minutes: int
    focus: Focus
    tags: list[str] = Field(default_factory=list)
    resources: dict[str, Any] = Field(default_factory=dict)


# Slug and goal_id are permanent, so they can't be patched.
class NodeUpdate(BaseModel):
    parent_id: PyObjectId | None = None
    title: str | None = None
    description: str | None = None
    done_criteria: str | None = None
    optional: bool | None = None
    score: int | None = None
    test_id: PyObjectId | None = None
    required_open_score: int | None = None
    est_minutes: int | None = None
    focus: Focus | None = None
    tags: list[str] | None = None
    resources: dict[str, Any] | None = None


@router.get("")
async def list_nodes() -> list[Node]:
    return await nodes.list_nodes()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_node(body: NodeCreate) -> Node:
    return await nodes.create_node(Node.model_validate(body.model_dump()))


@router.patch("/{node_id}")
async def update_node(node_id: PyObjectId, body: NodeUpdate) -> Node:
    return await nodes.update_node(node_id, body.model_dump(exclude_unset=True))


# Stand-in until sessions (M3) are what complete a node.
@router.post("/{node_id}/complete")
async def complete_node(node_id: PyObjectId) -> Node:
    return await nodes.complete_node(node_id)


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(node_id: PyObjectId) -> None:
    await nodes.delete_node(node_id)
