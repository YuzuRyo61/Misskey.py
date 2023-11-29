from .sync_base import Misskey as Base
from .schemas import (
    MisskeyMeDetailed,
    MisskeyMeDetailedSchema,
)

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def i(self) -> MisskeyMeDetailed:
        return MisskeyMeDetailedSchema().load(
            self._api_request(endpoint="/api/i"))
