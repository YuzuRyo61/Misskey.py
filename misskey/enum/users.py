from enum import Enum

__all__ = (
    "UsersSortEnum",
    "UsersStateEnum",
    "UsersOriginEnum",
)


class UsersSortEnum(Enum):
    DESCENDING_FOLLOWER = "+follower"
    ASCENDING_FOLLOWER = "-follower"
    DESCENDING_CREATED_AT = "+createdAt"
    ASCENDING_CREATED_AT = "-createdAt"
    DESCENDING_UPDATED_AT = "+updatedAt"
    ASCENDING_UPDATED_AT = "-updatedAt"


class UsersStateEnum(Enum):
    ALL = "all"
    ALIVE = "alive"


class UsersOriginEnum(Enum):
    COMBINED = "combined"
    LOCAL = "local"
    REMOTE = "remote"
