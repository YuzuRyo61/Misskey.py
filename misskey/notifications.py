from typing import Optional

from .sync_base import Misskey as Base

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def i_notifications(
        self, *,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        mark_as_read: bool = True,
        # TODO: Add enum
        include_types=None,  # Optional[List[...Enum]]
        exclude_types=None,  # Optional[List[...Enum]]
    ):  # TODO: Add return value (Add new schema)
        pass

    def i_notifications_grouped(
        self, *,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        mark_as_read: bool = True,
        # TODO: Add enum
        include_types=None,  # Optional[List[...Enum]]
        exclude_types=None,  # Optional[List[...Enum]]
    ):  # TODO: Add return value (Add new schema)
        raise NotImplementedError()

    def notifications_create(
        self, *,
        body: str,
        header: Optional[str] = None,
        icon: Optional[str] = None,
    ):
        raise NotImplementedError()

    def notifications_mark_all_as_read(self):
        raise NotImplementedError()

    def notifications_test_notification(self):
        raise NotImplementedError()
