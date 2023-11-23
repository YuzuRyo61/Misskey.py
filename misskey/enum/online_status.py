from enum import Enum

__all__ = (
    "MisskeyOnlineStatusEnum",
)


class MisskeyOnlineStatusEnum(Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    ACTIVE = "active"
    OFFLINE = "offline"
