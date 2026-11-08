from datetime import UTC, datetime

from bson import ObjectId

from app.algorithms.lifecycle import next_status
from app.db import MongoDatabase
from app.models.node import Node, NodeStatus
from app.models.prerequisite import Prerequisite


async def recompute_statuses(db: MongoDatabase, node_ids: list[ObjectId]) -> None:
    # Works in waves: whenever a node becomes done, its dependents are checked in
    # the next wave, so a completion cascades as far as it unlocks things. Each
    # node can become done only once and prerequisites are acyclic, so it ends.
    pending = node_ids
    while pending:
        newly_done: list[ObjectId] = []
        for node in await Node.list_by_ids(db, pending):
            prerequisites = await Prerequisite.list_for_node(db, node.id)
            prerequisite_nodes = await Node.list_by_ids(
                db, [prerequisite.prerequisite_node_id for prerequisite in prerequisites]
            )
            status = next_status(node, prerequisite_nodes)
            if status == node.status:
                continue
            completed_at = datetime.now(UTC) if status == NodeStatus.DONE else None
            await Node.replace(
                db, node.model_copy(update={"status": status, "completed_at": completed_at})
            )
            if status == NodeStatus.DONE:
                newly_done.append(node.id)
        pending = await Prerequisite.list_dependent_ids(db, newly_done) if newly_done else []
