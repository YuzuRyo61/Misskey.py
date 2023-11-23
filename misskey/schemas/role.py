from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

__all__ = (
    "MisskeyRole",
    "MisskeyRoleSchema",
)


@dataclass
class MisskeyRole:
    id: str
    name: str
    description: str
    is_moderator: bool
    is_administrator: bool
    display_order: int
    color: Optional[str] = None
    icon_url: Optional[str] = None


class MisskeyRoleSchema(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    color = fields.String(required=True, allow_none=True)
    icon_url = fields.String(
        data_key="iconUrl",
        required=True, allow_none=True)
    description = fields.String(required=True)
    is_moderator = fields.Boolean(data_key="isModerator", required=True)
    is_administrator = fields.Boolean(
        data_key="isAdministrator", required=True)
    display_order = fields.Integer(data_key="displayOrder", required=True)

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MisskeyRole(**data)

    class Meta:
        unknown = INCLUDE
