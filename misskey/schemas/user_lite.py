import datetime
from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, INCLUDE

__all__ = (
    "MisskeyUserLite",
    "MisskeyUserLiteSchema",
)


@dataclass
class MisskeyUserLite:
    id: str
    username: str
    host: Optional[str] = None
    name: Optional[str] = None


class MisskeyUserLiteSchema(Schema):
    id = fields.String(required=True)
    username = fields.String(required=True)
    host = fields.String()
    name = fields.String(allow_none=True)

    class Meta:
        unknown = INCLUDE
