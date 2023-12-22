import inspect
from dataclasses import dataclass, field as dc_field
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

__all__ = (
    "UserLite",
    "UserLiteSchema",
)


@dataclass
class UserLite:
    id: str
    username: str
    host: Optional[str] = None
    name: Optional[str] = None

    _extra: dict = dc_field(default_factory=dict)

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


class UserLiteSchema(Schema):
    id = fields.String(required=True)
    username = fields.String(required=True)
    host = fields.String()
    name = fields.String(allow_none=True)

    class Meta:
        unknown = INCLUDE

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return UserLite.from_dict(data)
