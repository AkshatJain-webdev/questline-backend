from collections import defaultdict

from bson import ObjectId

from app.models.prerequisite import Prerequisite


def would_create_cycle(
    prerequisites: list[Prerequisite], node_id: ObjectId, prerequisite_node_id: ObjectId
) -> bool:
    # A loop forms exactly when prerequisite_node_id already depends on node_id (or is it).
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
