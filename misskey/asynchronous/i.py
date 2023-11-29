from .base import AsyncMisskey as Base
from misskey.schemas import (
    MeDetailed,
    MeDetailedSchema
)

__all__ = (
    "AsyncMisskey",
)


class AsyncMisskey(Base):
    async def i(self) -> MeDetailed:
        return MeDetailedSchema().load(
            await self._api_request(endpoint="/api/i"))
