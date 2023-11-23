from dataclasses import dataclass

from marshmallow import Schema, post_load, INCLUDE


__all__ = (
    "MisskeyPage",
    "MisskeyPageSchema",
)


@dataclass
class MisskeyPage:
    id: str


class MisskeyPageSchema(Schema):
    pass

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MisskeyPage(**data)

    class Meta:
        unknown = INCLUDE
