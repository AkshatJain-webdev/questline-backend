from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class Focus(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    DEEP = "deep"


class NodeStatus(StrEnum):
    LOCKED = "locked"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ABANDONED = "abandoned"


class Node(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId | None = Field(default=None, alias="_id")
    # Human-readable id like "hld-caching-01", used in commit messages.
    slug: str
    goal_id: PyObjectId
    # Display tree only; has no effect on unlocking (that's Prerequisite).
    parent_id: PyObjectId | None = None
    title: str
    description: str
    # Output-based target the user self-reports against when ending a session.
    done_criteria: str
    # Bonus work: the parent can complete without it (no auto-created Prerequisite).
    optional: bool = False
    # What this node is worth, once done, to anything that depends on it.
    score: int = 1
    # If set, this node can only reach done once that test is passed.
    test_id: PyObjectId | None = None
    # Unlocks once the done prerequisites' scores add up to this; None = all of them.
    required_open_score: int | None = None
    est_minutes: int
    # Energy and concentration needed, combined.
    focus: Focus
    # Controlled vocabulary shared across nodes; keywords are free-form.
    tags: list[str] = Field(default_factory=list)
    # Free-form, generated when the node is created.
    keywords: list[str] = Field(default_factory=list)
    # Vector of title + description + tags, for semantic search.
    embedding: list[float] | None = None
    status: NodeStatus = NodeStatus.LOCKED
    abandon_count: int = 0
    # Links to material for working on this node.
    resources: dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime | None = None
