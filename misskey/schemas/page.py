from dataclasses import dataclass

from marshmallow import Schema, post_load, INCLUDE


__all__ = (
    "Page",
    "PageSchema",
)


@dataclass
class Page:
    id: str
    # TODO: Add properties


class PageSchema(Schema):
    pass
    # TODO: Add properties

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return Page(**data)

    class Meta:
        unknown = INCLUDE
