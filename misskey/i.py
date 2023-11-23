from .sync_base import Misskey as Base
from .schemas import (
    MeDetailed,
    MeDetailedSchema,
)


class Misskey(Base):
    def i(self) -> MeDetailed:
        return MeDetailedSchema().load(self._api_request(endpoint="/api/i"))
