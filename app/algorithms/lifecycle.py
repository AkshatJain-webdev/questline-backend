from app.algorithms.unlock import is_unlocked
from app.models.node import Node, NodeStatus


def next_status(node: Node, prerequisite_nodes: list[Node]) -> NodeStatus:
    # Done never reverts, and in_progress/abandoned belong to sessions.
    if node.status not in (NodeStatus.LOCKED, NodeStatus.OPEN):
        return node.status
    if not is_unlocked(node, prerequisite_nodes):
        return NodeStatus.LOCKED

    # A rollup has no work of its own, so it's done the moment it opens.
    is_rollup = any(
        prerequisite.parent_id == node.id and not prerequisite.optional
        for prerequisite in prerequisite_nodes
    )
    return NodeStatus.DONE if is_rollup else NodeStatus.OPEN
