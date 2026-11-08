from datetime import date, datetime, time
from typing import Annotated, Any

from bson import ObjectId
from pydantic import PlainSerializer, PlainValidator, SerializationInfo, WithJsonSchema


def _to_object_id(value: Any) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise ValueError(f"{value!r} is not a valid ObjectId")


# JSON-only: model_dump() keeps a real ObjectId for pymongo; API responses get a string.
PyObjectId = Annotated[
    ObjectId,
    PlainValidator(_to_object_id),
    PlainSerializer(str, when_used="json"),
    WithJsonSchema({"type": "string"}),
]


def _serialize_date(value: date, info: SerializationInfo) -> datetime | str:
    if info.mode_is_json():
        return value.isoformat()
    return datetime.combine(value, time())


# BSON has no date type, so it's stored as a midnight datetime and read back as a date.
MongoDate = Annotated[
    date,
    PlainSerializer(_serialize_date),
    WithJsonSchema({"type": "string", "format": "date"}),
]
