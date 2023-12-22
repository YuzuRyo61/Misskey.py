from enum import Enum


__all__ = (
    "FFVisibilityEnum",
)


class FFVisibilityEnum(Enum):
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"
