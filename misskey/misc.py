from typing import Optional, List

from .sync_base import Misskey as Base
from .schemas import AnnouncementsSchema, Announcements
from .schemas.arguments import AnnouncementsArgumentsSchema

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def endpoints(self) -> List[str]:
        return self._api_request(endpoint="/api/endpoints")

    def announcements(
        self, *,
        limit: int = 10,
        with_unreads: bool = False,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> Announcements:
        payload_dict = {
            "limit": limit,
            "with_unreads": with_unreads,
        }
        if since_id is not None:
            payload_dict["since_id"] = since_id
        if until_id is not None:
            payload_dict["until_id"] = until_id

        payload = AnnouncementsArgumentsSchema().dump(payload_dict)

        return AnnouncementsSchema().load(
            self._api_request(endpoint="/api/announcements", params=payload),
            many=True)
