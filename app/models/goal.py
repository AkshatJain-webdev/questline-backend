from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import PyObjectId


class Goal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId | None = Field(default=None, alias="_id")
    title: str
    description: str
    color: str
    # Minimum minutes per week before the goal counts as neglected.
    weekly_min_minutes: int = 120
    target_date: date | None = None
    archived: bool = False
