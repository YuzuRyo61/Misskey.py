from enum import Enum

__all__ = (
    "DriveFilesSortEnum",
)


class DriveFilesSortEnum(Enum):
    DESCENDING_CREATED_AT = "+createdAt"
    ASCENDING_CREATED_AT = "-createdAt"
    DESCENDING_NAME = "+name"
    ASCENDING_NAME = "-name"
    DESCENDING_SIZE = "+size"
    ASCENDING_SIZE = "-size"
