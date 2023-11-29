from dataclasses import dataclass
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


class MiAuthResultSchema(Schema):
    ok = fields.Bool(required=True)
    token = fields.String(required=False)
    user = fields.Nested(UserDetailedSchema(), required=False)

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MiAuthResult(**data)

    class Meta:
        unknown = INCLUDE
