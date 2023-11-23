from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load

__all__ = (
    "MeDetailed",
    "MeDetailedSchema",
)


@dataclass
class MeDetailed:
    id: str
    username: str
    host: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_blurhash: Optional[str] = None


class MeDetailedSchema(Schema):
    id = fields.String(required=True)
    username = fields.String(required=True)
    host = fields.String()
    name = fields.String()
    avatar_url = fields.String(data_key="avatarUrl")
    avatar_blurhash = fields.String(data_key="avatar_blurhash")

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MeDetailed(**data)
