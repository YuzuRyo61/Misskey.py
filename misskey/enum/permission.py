from typing import List
from enum import Enum

__all__ = (
    "MisskeyPermissionEnum",
)


class MisskeyPermissionEnum(Enum):
    READ_ACCOUNT = "read:account"
    WRITE_ACCOUNT = "write:account"
    READ_BLOCKS = "read:blocks"
    WRITE_BLOCKS = "write:blocks"
    READ_DRIVE = "read:drive"
    WRITE_DRIVE = "write:drive"
    READ_FAVORITES = "read:favorites"
    WRITE_FAVORITES = "write:favorites"
    READ_FOLLOWING = "read:following"
    WRITE_FOLLOWING = "write:following"
    READ_MESSAGING = "read:messaging"
    WRITE_MESSAGING = "write:messaging"
    READ_MUTES = "read:mutes"
    WRITE_MUTES = "write:mutes"
    WRITE_NOTES = "write:notes"
    READ_NOTIFICATIONS = "read:notifications"
    WRITE_NOTIFICATIONS = "write:notifications"
    WRITE_REACTIONS = "write:reactions"
    WRITE_VOTES = "write:votes"
    READ_PAGES = "read:pages"
    WRITE_PAGES = "write:pages"
    WRITE_PAGE_LIKES = "write:page-likes"
    READ_PAGE_LIKES = "read:page-likes"
    WRITE_GALLERY_LIKES = "write:gallery-likes"
    READ_GALLERY_LIKES = "read:gallery-likes"

    @classmethod
    def all(cls) -> List[str]:
        return [i.value for i in cls]

    @classmethod
    def read_only(cls) -> List[str]:
        return [i.value for i in cls if i.value.startswith("read:")]

    @classmethod
    def write_only(cls) -> List[str]:
        return [i.value for i in cls if i.value.startswith("write:")]
