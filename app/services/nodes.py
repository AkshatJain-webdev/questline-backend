from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.db import MongoDatabase
from app.models.goal import Goal
from app.models.node import Node, NodeStatus
from app.models.prerequisite import Prerequisite
from app.services.errors import ConflictError, NotFoundError
from app.services.lifecycle import recompute_statuses
from app.services.prerequisites import add_prerequisite


def _auto_prerequisite_parent_id(node: Node) -> ObjectId | None:
    # A non-optional child must be done before its parent can open. Optional
    # children never gate their parent.
    return None if node.optional else node.parent_id


async def _check_parent(db: MongoDatabase, node: Node) -> None:
    if node.parent_id is None:
        return
    parent = await Node.get(db, node.parent_id)
    if parent is None:
        raise NotFoundError(f"Parent node {node.parent_id} not found")
    if parent.goal_id != node.goal_id:
        raise ConflictError("A node's parent must belong to the same goal")

    # Walking up from the new parent and reaching this node means it would become
    # its own ancestor, looping the display tree.
    ancestor: Node | None = parent
    while ancestor is not None:
        if ancestor.id == node.id:
            raise ConflictError("A node can't be moved under itself or one of its descendants")
        ancestor = (
            await Node.get(db, ancestor.parent_id) if ancestor.parent_id is not None else None
        )


async def create_node(db: MongoDatabase, node: Node) -> Node:
    if await Goal.get(db, node.goal_id) is None:
        raise NotFoundError(f"Goal {node.goal_id} not found")
    await _check_parent(db, node)

    try:
        created = await Node.insert(db, node)
    except DuplicateKeyError:
        raise ConflictError(f"Slug {node.slug!r} is already taken") from None

    parent_id = _auto_prerequisite_parent_id(created)
    if parent_id is not None:
        await add_prerequisite(db, parent_id, created.id)
    await recompute_statuses(db, [created.id])
    return await get_node(db, created.id)


async def get_node(db: MongoDatabase, node_id: ObjectId) -> Node:
    node = await Node.get(db, node_id)
    if node is None:
        raise NotFoundError(f"Node {node_id} not found")
    return node


async def update_node(db: MongoDatabase, node_id: ObjectId, changes: dict[str, Any]) -> Node:
    current = await get_node(db, node_id)
    updated = Node.model_validate(current.model_dump() | changes)
    if updated.goal_id != current.goal_id:
        raise ConflictError("A node can't be moved to another goal")
    if updated.slug != current.slug:
        raise ConflictError("A node's slug is permanent; it's referenced from commit messages")
    await _check_parent(db, updated)

    old_parent_id = _auto_prerequisite_parent_id(current)
    new_parent_id = _auto_prerequisite_parent_id(updated)
    # Adding the new prerequisite goes first: it's the only step that can fail (a
    # cycle), so a failure leaves nothing half-changed.
    if new_parent_id is not None and new_parent_id != old_parent_id:
        await add_prerequisite(db, new_parent_id, node_id)
    await Node.replace(db, updated)
    if old_parent_id is not None and old_parent_id != new_parent_id:
        await Prerequisite.delete(db, old_parent_id, node_id)

    # An edit can shift unlocking on both sides: this node's own threshold, its
    # score as its dependents see it, and the old parent it no longer gates.
    affected_ids = [node_id, *await Prerequisite.list_dependent_ids(db, [node_id])]
    if old_parent_id is not None:
        affected_ids.append(old_parent_id)
    await recompute_statuses(db, affected_ids)
    return await get_node(db, node_id)


async def complete_node(db: MongoDatabase, node_id: ObjectId) -> Node:
    node = await get_node(db, node_id)
    if node.status != NodeStatus.OPEN:
        raise ConflictError(f"Only an open node can be completed; this one is {node.status}")
    completed = node.model_copy(
        update={"status": NodeStatus.DONE, "completed_at": datetime.now(UTC)}
    )
    await Node.replace(db, completed)
    await recompute_statuses(db, await Prerequisite.list_dependent_ids(db, [node_id]))
    return completed


async def delete_node(db: MongoDatabase, node_id: ObjectId) -> None:
    await get_node(db, node_id)
    if await Node.has_children(db, node_id):
        raise ConflictError("Delete or move this node's children first")
    dependent_ids = await Prerequisite.list_dependent_ids(db, [node_id])
    await Prerequisite.delete_involving_nodes(db, [node_id])
    await Node.delete(db, node_id)
    await recompute_statuses(db, dependent_ids)
