import datetime
from typing import List, Optional

from .sync_base import Misskey as Base
from .schemas import (
    CreatedNoteSchema,
    CreatedNote,
    Note,
    NoteSchema,
)
from .schemas.arguments import (
    NotesCreateArgumentsSchema,
    NotesLocalTimelineArgumentsSchema,
)
from .enum import (
    VisibilityEnum,
    ReactionAcceptanceEnum,
)
from .dict import PollCreateDict

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def notes_create(
        self, *,
        visibility: VisibilityEnum =
        VisibilityEnum.PUBLIC,
        visible_user_ids: Optional[List[str]] = None,
        cw: Optional[str] = None,
        local_only: bool = False,
        reaction_acceptance: ReactionAcceptanceEnum =
        ReactionAcceptanceEnum.NULL,
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

        payload = NotesCreateArgumentsSchema().dump(payload_dict)

        return CreatedNoteSchema().load(
            self._api_request(endpoint="/api/notes/create", params=payload))

    def notes_show(self, *, note_id: str) -> Note:
        payload = {
            "noteId": note_id,
        }
        return NoteSchema().load(
            self._api_request(endpoint="/api/notes/show", params=payload))

    def notes_delete(self, *, note_id: str) -> None:
        payload = {
            "noteId": note_id,
        }
        self._api_request(endpoint="/api/notes/delete", params=payload)

    def notes_reactions_create(
        self, *,
        note_id: str,
        reaction: str,
    ) -> None:
        payload = {
            "noteId": note_id,
            "reaction": reaction,
        }
        self._api_request(
            endpoint="/api/notes/reactions/create", params=payload)

    def notes_reactions_delete(
        self, *,
        note_id: str,
    ) -> None:
        payload = {
            "noteId": note_id,
        }
        self._api_request(
            endpoint="/api/notes/reactions/delete", params=payload)

    def notes_local_timeline(
        self, *,
        with_files: bool = False,
        with_renotes: bool = False,
        with_replies: bool = False,
        exclude_nsfw: bool = False,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        # TODO: API is int, so convert
        since_date: Optional[datetime.datetime] = None,
        # TODO: API is int, so convert
        until_date: Optional[datetime.datetime] = None,
    ) -> List[Note]:
        payload_dict = {
            "with_files": with_files,
            "with_renotes": with_renotes,
            "with_replies": with_replies,
            "exclude_nsfw": exclude_nsfw,
            "limit": limit,
        }
        if since_id is not None:
            payload_dict["since_id"] = since_id
        if until_id is not None:
            payload_dict["until_id"] = until_id
        # if since_date is not None:
        #     payload_dict["since_date"] = since_date
        # if until_date is not None:
        #     payload_dict["until_date"] = until_date

        payload = NotesLocalTimelineArgumentsSchema().dump(payload_dict)

        return NoteSchema().load(
            self._api_request(
                endpoint="/api/notes/local-timeline", params=payload),
            many=True,
        )
