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
    created_at: datetime.datetime
    username: str
    host: Optional[str] = None


class MisskeyUserLiteSchema(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime(data_key="createdAt", required=True)
    username = fields.String(required=True)
    host = fields.String()

    class Meta:
        unknown = INCLUDE
