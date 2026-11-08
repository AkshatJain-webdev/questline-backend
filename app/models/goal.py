from typing import ClassVar

from app.models.base import AppDBModel
from app.models.common import MongoDate


class Goal(AppDBModel):
    COLLECTION: ClassVar[str] = "goals"

    title: str
    description: str
    color: str
    # Minimum minutes per week before the goal counts as neglected.
    weekly_min_minutes: int = 120
    target_date: MongoDate | None = None
    archived: bool = False
