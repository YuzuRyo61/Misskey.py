import inspect
import datetime
from dataclasses import dataclass
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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        })


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
