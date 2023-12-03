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
    def drive(self):
        # TODO
        raise NotImplementedError()

    def drive_files_create(
        self, *,
        file,
        folder_id: Optional[str] = None,
        name: Optional[str] = None,
        comment: Optional[str] = None,
        is_sensitive: bool = False,
        force: bool = False,
    ) -> DriveFile:
        # TODO: This API has a special behavior, so process it accordingly.
        raise NotImplementedError()

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

    def drive_files_delete(
        self, *,
        file_id: str,
    ):
        payload = {
            "fileId": file_id,
        }
        self._api_request(
            endpoint="/api/drive/files/delete", params=payload)

    def drive_files_update(
        self, *,
        file_id: str,
        # TODO: Think about how you want to null
        folder_id: Optional[str] = None,
        name: Optional[str] = None,
        is_sensitive: Optional[bool] = None,
        comment: Optional[bool] = None,
    ):
        # TODO
        raise NotImplementedError()
