from enum import Enum

__all__ = (
    "OnlineStatusEnum",
)


class OnlineStatusEnum(Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    ACTIVE = "active"
    OFFLINE = "offline"
