from typing import ClassVar, Self

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.db import MongoDatabase
from app.models.common import PyObjectId


class AppDBModel(BaseModel):
    COLLECTION: ClassVar[str]
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId | None = Field(default=None, alias="_id")

    @classmethod
    async def insert(cls, db: MongoDatabase, model: Self) -> Self:
        # id is left out so Mongo assigns _id itself.
        result = await db[cls.COLLECTION].insert_one(model.model_dump(exclude={"id"}))
        return model.model_copy(update={"id": result.inserted_id})

    @classmethod
    async def replace(cls, db: MongoDatabase, model: Self) -> None:
        await db[cls.COLLECTION].replace_one({"_id": model.id}, model.model_dump(exclude={"id"}))

    @classmethod
    async def get(cls, db: MongoDatabase, model_id: ObjectId) -> Self | None:
        document = await db[cls.COLLECTION].find_one({"_id": model_id})
        return cls.model_validate(document) if document else None

    @classmethod
    async def list_all(cls, db: MongoDatabase) -> list[Self]:
        return [cls.model_validate(document) async for document in db[cls.COLLECTION].find()]

    @classmethod
    async def delete(cls, db: MongoDatabase, model_id: ObjectId) -> bool:
        result = await db[cls.COLLECTION].delete_one({"_id": model_id})
        return result.deleted_count == 1
