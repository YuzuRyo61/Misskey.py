import inspect
from dataclasses import dataclass, field as dc_field

from marshmallow import Schema, fields, post_load, INCLUDE


__all__ = (
    "Page",
    "PageSchema",
)


@dataclass
class Page:
    id: str
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


class PageSchema(Schema):
    id = fields.String(required=True)
    # TODO: Add properties

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return Page.from_dict(data)

    class Meta:
        unknown = INCLUDE
