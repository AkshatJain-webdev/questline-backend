from typing import Annotated, Any

from bson import ObjectId
from pydantic import PlainSerializer, PlainValidator, WithJsonSchema


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
