import inspect
import datetime
from dataclasses import dataclass, field as dc_field
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

__all__ = (
    "UserDetailed",
    "UserDetailedSchema",
)


@dataclass
class UserDetailed:
    id: str
    created_at: datetime.datetime
    username: str
    host: Optional[str] = None

    _extra: dict = dc_field(default_factory=dict)
    # TODO: Misskey API documentation information is out of date

    @classmethod
    def from_dict(cls, data: dict):
        payload = {
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        }
        payload["_extra"] = {
            k: v for k, v in data.items()
            if k not in inspect.signature(cls).parameters
        }
        return cls(**payload)


class UserDetailedSchema(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime(data_key="createdAt", required=True)
    username = fields.String(required=True)
    host = fields.String(allow_none=True)

    class Meta:
        unknown = INCLUDE

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return UserDetailed.from_dict(data)
