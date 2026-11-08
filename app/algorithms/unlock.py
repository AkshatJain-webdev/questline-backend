from app.models.node import Node, NodeStatus


def is_unlocked(node: Node, prerequisite_nodes: list[Node]) -> bool:
    done_score = sum(
        prerequisite.score
        for prerequisite in prerequisite_nodes
        if prerequisite.status == NodeStatus.DONE
    )
    # None means "all of them", so with no prerequisites at all a node is open.
    required_score = (
        sum(prerequisite.score for prerequisite in prerequisite_nodes)
        if node.required_open_score is None
        else node.required_open_score
    )
    return done_score >= required_score
