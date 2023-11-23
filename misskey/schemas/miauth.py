from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

from .user import (
    MisskeyUserSchema,
    MisskeyUser,
)

__all__ = (
    "MiAuthResult",
    "MiAuthResultSchema",
)


@dataclass
class MiAuthResult:
    ok: bool
    token: Optional[str] = None
    user: Optional[MisskeyUser] = None


class MiAuthResultSchema(Schema):
    ok = fields.Bool(required=True)
    token = fields.String(required=False)
    user = fields.Nested(MisskeyUserSchema(), required=False)

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MiAuthResult(**data)

    class Meta:
        unknown = INCLUDE
