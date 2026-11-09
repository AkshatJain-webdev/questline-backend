import asyncio
import json
from pathlib import Path

from app.db import client, create_indexes
from app.models.goal import Goal
from app.models.node import Node
from app.services.goals import create_goal
from app.services.nodes import create_node
from app.services.prerequisites import add_prerequisite

SEED_PATH = Path(__file__).with_name("interview_prep.json")


async def main() -> None:
    try:
        await create_indexes()
        # Goals have no unique key, so loading twice would duplicate them.
        if await Goal.list_all():
            raise SystemExit("The database already has goals; seed only an empty database.")

        # The file has "goals", "nodes" and "prerequisites" lists; nodes name their goal by title.
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))

        goal_ids_by_title = {}
        for goal_fields in seed["goals"]:
            goal = await create_goal(Goal(**goal_fields))
            goal_ids_by_title[goal.title] = goal.id

        # A parent must come before its children in the file, since create_node checks it exists.
        node_ids_by_slug = {}
        for node_fields in seed["nodes"]:
            goal_title = node_fields.pop("goal")
            parent_slug = node_fields.pop("parent", None)
            node = await create_node(
                Node(
                    goal_id=goal_ids_by_title[goal_title],
                    parent_id=node_ids_by_slug[parent_slug] if parent_slug else None,
                    **node_fields,
                )
            )
            node_ids_by_slug[node.slug] = node.id

        for prerequisite in seed["prerequisites"]:
            await add_prerequisite(
                node_ids_by_slug[prerequisite["node"]],
                node_ids_by_slug[prerequisite["prerequisite"]],
            )

        print(
            f"Created {len(seed['goals'])} goals, {len(seed['nodes'])} nodes "
            f"and {len(seed['prerequisites'])} prerequisites"
        )
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
