from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class Prerequisite(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId | None = Field(default=None, alias="_id")
    # prerequisite_node_id must be done before node_id can open.
    node_id: PyObjectId
    prerequisite_node_id: PyObjectId
