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


# json-only: model_dump() keeps a real ObjectId for passing straight into pymongo; 
# only JSON output (API responses) gets the string form.
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


# BSON has no date-only type, so model_dump() turns a date into a midnight
# datetime for Mongo; Pydantic turns it back into a date when the document is read.
MongoDate = Annotated[
    date,
    PlainSerializer(_serialize_date),
    WithJsonSchema({"type": "string", "format": "date"}),
]
