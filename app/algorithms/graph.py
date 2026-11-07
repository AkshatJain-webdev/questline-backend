from collections import defaultdict

from bson import ObjectId

from app.models.prerequisite import Prerequisite


def would_create_cycle(
    prerequisites: list[Prerequisite], node_id: ObjectId, prerequisite_node_id: ObjectId
) -> bool:
    # The new edge makes node_id depend on prerequisite_node_id. That closes a loop
    # exactly when prerequisite_node_id already depends, directly or through other
    # nodes, on node_id. A node depending on itself is the shortest such loop.
    depends_on: dict[ObjectId, list[ObjectId]] = defaultdict(list)
    for prerequisite in prerequisites:
        depends_on[prerequisite.node_id].append(prerequisite.prerequisite_node_id)

    to_visit = [prerequisite_node_id]
    visited: set[ObjectId] = set()
    while to_visit:
        current = to_visit.pop()
        if current == node_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        to_visit.extend(depends_on[current])
    return False
