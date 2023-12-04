from typing import Optional, List

from .sync_base import Misskey as Base
from .schemas import (
    Drive,
    DriveSchema,
    DriveFile,
    DriveFileSchema,
)

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def drive(self) -> Drive:
        return DriveSchema().load(self._api_request(endpoint="/api/drive"))

    def drive_files(
        self, *,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        type: Optional[str] = None,
        sort,  # TODO: Define enum
    ) -> List[DriveFile]:
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

    def drive_files_upload_from_url(
        self, *,
        url: str,
        folder_id: Optional[str] = None,
        is_sensitive: bool = False,
        comment: Optional[str] = None,
        marker: Optional[str] = None,
        force: bool = False,
    ) -> None:
        # TODO
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
    ) -> None:
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
    ) -> DriveFile:
        # TODO
        raise NotImplementedError()

    def drive_files_find(
        self, *,
        name: str,
        folder_id: Optional[str] = None,
    ) -> List[DriveFile]:
        # TODO
        raise NotImplementedError()

    def drive_files_find_by_hash(
        self, *,
        md5: str,
    ) -> List[DriveFile]:
        # TODO
        raise NotImplementedError()

    def drive_files_check_existence(
        self, *,
        md5: str,
    ) -> bool:
        # TODO
        raise NotImplementedError()

    def drive_files_attached_notes(
        self, *,
        file_id: str,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[DriveFile]:
        # TODO
        raise NotImplementedError()
