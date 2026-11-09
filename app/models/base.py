from typing import ClassVar, Self

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.db import db
from app.models.common import PyObjectId


class AppDBModel(BaseModel):
    COLLECTION: ClassVar[str]
    model_config = ConfigDict(populate_by_name=True)

    # Generated here, as pymongo would anyway, so a model always has an id; stored as _id.
    id: PyObjectId = Field(default_factory=ObjectId, validation_alias="_id")

    @classmethod
    async def insert(cls, model: Self) -> Self:
        await db[cls.COLLECTION].insert_one({"_id": model.id, **model.model_dump(exclude={"id"})})
        return model

    @classmethod
    async def replace(cls, model: Self) -> None:
        await db[cls.COLLECTION].replace_one({"_id": model.id}, model.model_dump(exclude={"id"}))

    @classmethod
    async def get(cls, model_id: ObjectId) -> Self | None:
        document = await db[cls.COLLECTION].find_one({"_id": model_id})
        return cls.model_validate(document) if document else None

    @classmethod
    async def list_all(cls) -> list[Self]:
        return [cls.model_validate(document) async for document in db[cls.COLLECTION].find()]

    @classmethod
    async def delete(cls, model_id: ObjectId) -> bool:
        result = await db[cls.COLLECTION].delete_one({"_id": model_id})
        return result.deleted_count == 1

    @classmethod
    async def delete_all(cls) -> None:
        await db[cls.COLLECTION].delete_many({})
