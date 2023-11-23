from enum import Enum


__all__ = (
    "MisskeyFFVisibilityEnum",
)


class MisskeyFFVisibilityEnum(Enum):
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"
