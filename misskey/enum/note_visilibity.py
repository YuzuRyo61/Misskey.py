from enum import Enum

__all__ = (
    "MisskeyNoteVisibilityEnum",
)


class MisskeyNoteVisibilityEnum(Enum):
    PUBLIC = "public"
    HOME = "home"
    FOLLOWERS = "followers"
    SPECIFIED = "specified"
