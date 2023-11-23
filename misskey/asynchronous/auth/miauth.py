import aiohttp

from misskey.schemas import (
    MiAuthResult,
    MiAuthResultSchema,
)
from misskey.auth.miauth_base import MiAuthBase

__all__ = (
    "AsyncMiAuth",
)


class AsyncMiAuth(MiAuthBase):
    session: aiohttp.ClientSession

    def __init__(
        self, *,
        session: aiohttp.ClientSession,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session = session

    async def auth(self) -> MiAuthResult:
        async with self.session.post(
            f"{self.address}/api/miauth/{self.session_id}/check",
                json={},
                headers={"Content-Type": "application/json"},
                raise_for_status=True) as res:
            return MiAuthResultSchema().load(await res.json())
