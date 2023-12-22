from enum import Enum

__all__ = (
    "VisibilityEnum",
)


class VisibilityEnum(Enum):
    PUBLIC = "public"
    HOME = "home"
    FOLLOWERS = "followers"
    SPECIFIED = "specified"
