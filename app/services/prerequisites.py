from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.algorithms.graph import would_create_cycle
from app.models.node import Node
from app.models.prerequisite import Prerequisite
from app.services.errors import ConflictError, NotFoundError
from app.services.lifecycle import recompute_statuses


async def add_prerequisite(node_id: ObjectId, prerequisite_node_id: ObjectId) -> Prerequisite:
    for required_node_id in (node_id, prerequisite_node_id):
        if await Node.get(required_node_id) is None:
            raise NotFoundError(f"Node {required_node_id} not found")

    existing = await Prerequisite.list_all()
    if would_create_cycle(existing, node_id, prerequisite_node_id):
        raise ConflictError("This prerequisite would create a cycle")

    prerequisite = Prerequisite(node_id=node_id, prerequisite_node_id=prerequisite_node_id)
    try:
        created = await Prerequisite.insert(prerequisite)
    except DuplicateKeyError:
        raise ConflictError("This prerequisite already exists") from None
    await recompute_statuses([node_id])
    return created


async def remove_prerequisite(node_id: ObjectId, prerequisite_node_id: ObjectId) -> None:
    # This edge is controlled by the child's `optional` flag; change that instead.
    prerequisite_node = await Node.get(prerequisite_node_id)
    if (
        prerequisite_node is not None
        and prerequisite_node.parent_id == node_id
        and not prerequisite_node.optional
    ):
        raise ConflictError(
            "This prerequisite comes from a non-optional child; mark the child optional instead"
        )

    if not await Prerequisite.delete_pair(node_id, prerequisite_node_id):
        raise NotFoundError("Prerequisite not found")
    await recompute_statuses([node_id])
