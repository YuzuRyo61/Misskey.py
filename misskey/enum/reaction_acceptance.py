from enum import Enum

__all__ = (
    "MisskeyReactionAcceptanceEnum",
)


class MisskeyReactionAcceptanceEnum(Enum):
    NULL = None
    LIKE_ONLY = "likeOnly"
    LIKE_ONLY_FOR_REMOTE = "likeOnlyForRemote"
    NON_SENSITIVE_ONLY = "nonSensitiveOnly"
    NON_SENSITIVE_ONLY_FOR_LOCAL_LIKE_ONLY_FOR_REMOTE = \
        "nonSensitiveOnlyForLocalLikeOnlyForRemote"
