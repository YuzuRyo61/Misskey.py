from .base import AsyncMisskey as Base

from misskey.schemas import (
    Meta,
    MetaSchema,
)

__all__ = (
    "AsyncMisskey",
)


class AsyncMisskey(Base):
    async def meta(self, *, detail: bool = False) -> Meta:
        payload = {
            "detail": detail,
        }
        return MetaSchema().load(
            await self._api_request(endpoint="/api/meta", params=payload))
