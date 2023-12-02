from typing import Optional

from .sync_base import Misskey as Base
from .schemas import (
    DriveFile,
    DriveFileSchema,
)

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def drive_files_show(
        self, *,
        file_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> DriveFile:
        payload = {}
        if file_id is not None:
            payload["fileId"] = file_id
        if url is not None:
            payload["url"] = url

        return DriveFileSchema().load(
            self._api_request(
                endpoint="/api/drive/files/show", params=payload))
