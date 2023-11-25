from .sync_base import Misskey as Base

from misskey.schemas import (
    MisskeyMeta,
    MisskeyMetaSchema,
)

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def meta(self, *, detail: bool = False) -> MisskeyMeta:
        payload = {
            "detail": detail,
        }
        return MisskeyMetaSchema().load(
            self._api_request(endpoint="/api/meta", params=payload))
