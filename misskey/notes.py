from typing import List, Optional

from .sync_base import Misskey as Base
from .schemas import (
    CreatedNoteSchema,
    CreatedNote,
)
from .schemas.arguments import (
    NotesCreateSchema,
)
from .enum import (
    MisskeyNoteVisibilityEnum,
    MisskeyReactionAcceptanceEnum,
)
from .dict import PollCreateDict

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def notes_create(
        self, *,
        visibility: MisskeyNoteVisibilityEnum =
        MisskeyNoteVisibilityEnum.PUBLIC,
        visible_user_ids: Optional[List[str]] = None,
        cw: Optional[str] = None,
        local_only: bool = False,
        reaction_acceptance: MisskeyReactionAcceptanceEnum =
        MisskeyReactionAcceptanceEnum.NULL,
        no_extract_mentions: bool = False,
        no_extract_hashtags: bool = False,
        no_extract_emojis: bool = False,
        reply_id: Optional[str] = None,
        renote_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        text: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        media_ids: Optional[List[str]] = None,
        poll: Optional[PollCreateDict] = None,
        **kwargs,
    ) -> CreatedNote:
        payload_dict = {
            "visibility": visibility,
            "cw": cw,
            "local_only": local_only,
            "reaction_acceptance": reaction_acceptance,
            "no_extract_mentions": no_extract_mentions,
            "no_extract_hashtags": no_extract_hashtags,
            "no_extract_emojis": no_extract_emojis,
            "reply_id": reply_id,
            "renote_id": renote_id,
            "channel_id": channel_id,
            "text": text,
        }
        if visible_user_ids is not None:
            payload_dict["visible_user_ids"] = visible_user_ids
        if file_ids is not None:
            payload_dict["file_ids"] = file_ids
        if media_ids is not None:
            payload_dict["media_ids"] = media_ids
        if poll is not None:
            payload_dict["poll"] = poll

        payload_dict.update(kwargs)

        payload = NotesCreateSchema().dump(payload_dict)

        return CreatedNoteSchema().load(
            self._api_request(endpoint="/api/notes/create", params=payload))

    def notes_delete(self, *, note_id: str) -> None:
        payload = {
            "noteId": note_id,
        }
        self._api_request(endpoint="/api/notes/delete", params=payload)
