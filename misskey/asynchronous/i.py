from .base import AsyncMisskey as Base
from misskey.schemas import (
    MisskeyMeDetailed,
    MisskeyMeDetailedSchema
)

__all__ = (
    "AsyncMisskey",
)


class AsyncMisskey(Base):
    async def i(self) -> MisskeyMeDetailed:
        return MisskeyMeDetailedSchema().load(
            await self._api_request(endpoint="/api/i"))
