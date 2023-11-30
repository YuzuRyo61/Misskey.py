import inspect
from dataclasses import dataclass, field as dc_field
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

__all__ = (
    "Role",
    "RoleSchema",
)


@dataclass
class Role:
    id: str
    name: str
    description: str
    is_moderator: bool
    is_administrator: bool
    display_order: int
    color: Optional[str] = None
    icon_url: Optional[str] = None

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


class RoleSchema(Schema):
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
        return Role.from_dict(data)

    class Meta:
        unknown = INCLUDE
