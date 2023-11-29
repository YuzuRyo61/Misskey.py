from .sync_base import Misskey as Base

from misskey.schemas import (
    Meta,
    MetaSchema,
)

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def meta(self, *, detail: bool = False) -> Meta:
        payload = {
            "detail": detail,
        }
        return MetaSchema().load(
            self._api_request(endpoint="/api/meta", params=payload))
