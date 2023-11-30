import inspect
from dataclasses import dataclass, field as dc_field
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

from .user_detailed import (
    UserDetailedSchema,
    UserDetailed,
)

__all__ = (
    "MiAuthResult",
    "MiAuthResultSchema",
)


@dataclass
class MiAuthResult:
    ok: bool
    token: Optional[str] = None
    user: Optional[UserDetailed] = None

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


class MiAuthResultSchema(Schema):
    ok = fields.Bool(required=True)
    token = fields.String(required=False)
    user = fields.Nested(UserDetailedSchema(), required=False)

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MiAuthResult.from_dict(**data)

    class Meta:
        unknown = INCLUDE
