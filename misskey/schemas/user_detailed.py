import datetime
from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, INCLUDE

__all__ = (
    "MisskeyUserDetailed",
    "MisskeyUserDetailedSchema",
)


@dataclass
class MisskeyUserDetailed:
    id: str
    created_at: datetime.datetime
    username: str
    host: Optional[str] = None


class MisskeyUserDetailedSchema(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime(data_key="createdAt", required=True)
    username = fields.String(required=True)
    host = fields.String()

    class Meta:
        unknown = INCLUDE
