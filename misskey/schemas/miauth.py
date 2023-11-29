from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

from .user_detailed import (
    MisskeyUserDetailedSchema,
    MisskeyUserDetailed,
)

__all__ = (
    "MiAuthResult",
    "MiAuthResultSchema",
)


@dataclass
class MiAuthResult:
    ok: bool
    token: Optional[str] = None
    user: Optional[MisskeyUserDetailed] = None


class MiAuthResultSchema(Schema):
    ok = fields.Bool(required=True)
    token = fields.String(required=False)
    user = fields.Nested(MisskeyUserDetailedSchema(), required=False)

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MiAuthResult(**data)

    class Meta:
        unknown = INCLUDE
