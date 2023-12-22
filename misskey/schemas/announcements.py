import inspect
import datetime
from typing import Optional
from dataclasses import dataclass, field as dc_field

from marshmallow import Schema, fields, post_load, INCLUDE


__all__ = (
    "Announcements",
    "AnnouncementsSchema",
)


@dataclass
class Announcements:
    id: str
    created_at: datetime.datetime
    text: str
    title: str
    updated_at: Optional[datetime.datetime] = None
    image_url: Optional[str] = None
    is_read: Optional[bool] = None
    # TODO: Misskey API documentation information is out of date

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


class AnnouncementsSchema(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime(required=True, data_key="createdAt")
    updated_at = fields.DateTime(
        required=True, allow_none=True, data_key="updatedAt")
    text = fields.String(required=True)
    title = fields.String(required=True)
    image_url = fields.String(
        required=True, allow_none=True, data_key="imageUrl")
    is_read = fields.Boolean(data_key="isRead")
    # TODO: Misskey API documentation information is out of date

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return Announcements.from_dict(data)

    class Meta:
        unknown = INCLUDE
