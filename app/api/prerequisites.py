from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import BaseModel

from app.models.common import PyObjectId
from app.models.prerequisite import Prerequisite
from app.services import prerequisites

router = APIRouter(prefix="/prerequisites", tags=["prerequisites"])


class PrerequisiteCreate(BaseModel):
    node_id: PyObjectId
    prerequisite_node_id: PyObjectId


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_prerequisite(body: PrerequisiteCreate) -> Prerequisite:
    return await prerequisites.add_prerequisite(body.node_id, body.prerequisite_node_id)


# Query parameters, since DELETE requests shouldn't carry a body.
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def remove_prerequisite(
    node_id: Annotated[PyObjectId, Query()],
    prerequisite_node_id: Annotated[PyObjectId, Query()],
) -> None:
    await prerequisites.remove_prerequisite(node_id, prerequisite_node_id)
