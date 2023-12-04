import inspect
import datetime
from dataclasses import dataclass, field as dc_field
from typing import Optional

from marshmallow import Schema, fields, post_load, INCLUDE

__all__ = (
    "Drive",
    "DriveSchema",
    "DriveFile",
    "DriveFileSchema",
)


@dataclass
class Drive:
    capacity: int
    usage: int

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


class DriveSchema(Schema):
    capacity = fields.Integer(required=True)
    usage = fields.Integer(required=True)

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data: dict, **kwargs):
        return Drive.from_dict(data)

    class Meta:
        unknown = INCLUDE


@dataclass
class DriveFile:
    id: str
    created_at: datetime.datetime
    name: str
    type: str
    md5: str
    size: str
    is_sensitive: bool
    blurhash: str
    url: str
    thumbnail_url: str
    comment: str
    folder_id: Optional[str] = None
    user_id: Optional[str] = None
    # TODO: Add properties

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


class DriveFileSchema(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime("iso", data_key="createdAt", required=True)
    name = fields.String(required=True)
    type = fields.String(required=True)
    md5 = fields.String(required=True)
    size = fields.Integer(required=True)
    is_sensitive = fields.Boolean(required=True, data_key="isSensitive")
    blurhash = fields.String(required=True, allow_none=True)
    # properties = fields.Nested(...)  # TODO
    url = fields.Url(allow_none=True, required=True)
    thumbnail_url = fields.Url(
        allow_none=True, required=True, data_key="thumbnailUrl")
    comment = fields.String(required=True, allow_none=True)
    folder_id = fields.String(
        required=True, allow_none=True, data_key="folderId")
    # folder = fields.Nested(...)  # TODO
    user_id = fields.String(required=True, allow_none=True, data_key="userId")
    # user = fields.Nested(...)  # TODO

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return DriveFile.from_dict(data)

    class Meta:
        unknown = INCLUDE
