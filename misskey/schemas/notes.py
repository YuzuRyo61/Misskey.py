from __future__ import annotations

import datetime
import inspect
from typing import Optional, List
from dataclasses import dataclass

from marshmallow import Schema, fields, post_load, INCLUDE

from misskey.enum import (
    MisskeyNoteVisibilityEnum,
    MisskeyReactionAcceptanceEnum,
)

__all__ = (
    "MisskeyCreatedNote",
    "MisskeyCreatedNoteSchema",
    "MisskeyNote",
    "MisskeyNoteSchema",
)


@dataclass
class MisskeyNote:
    id: str
    created_at: datetime.datetime
    visibility: MisskeyNoteVisibilityEnum
    renote_count: int
    replies_count: int
    deleted_at: Optional[datetime.datetime] = None
    text: Optional[str] = None
    cw: Optional[str] = None
    user_id: Optional[str] = None
    reply_id: Optional[str] = None
    renote_id: Optional[str] = None
    reply: Optional[MisskeyNote] = None
    renote: Optional[MisskeyNote] = None
    is_hidden: Optional[bool] = None
    mentions: Optional[List[str]] = None
    visible_user_ids: Optional[List[str]] = None
    file_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    channel_id: Optional[str] = None
    local_only: Optional[bool] = None
    reaction_acceptance: Optional[MisskeyReactionAcceptanceEnum] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        })


@dataclass
class MisskeyCreatedNote:
    created_note: MisskeyNote


# noinspection PyTypeChecker
class MisskeyNoteSchema(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime("iso", required=True, data_key="createdAt")
    deleted_at = fields.DateTime("iso", allow_none=True, data_key="deletedAt")
    text = fields.String(required=True, allow_none=True)
    cw = fields.String(allow_none=True)
    user_id = fields.String(required=True, data_key="userId")
    reply_id = fields.String(allow_none=True, data_key="replyId")
    renote_id = fields.String(allow_none=True, data_key="renoteId")
    reply = fields.Nested(
        lambda: MisskeyNoteSchema(exclude=("reply",)), allow_none=True)
    renote = fields.Nested(
        lambda: MisskeyNoteSchema(exclude=("renote",)), allow_none=True)
    is_hidden = fields.Boolean(data_key="isHidden")
    visibility = fields.Enum(
        MisskeyNoteVisibilityEnum, by_value=True, required=True)
    mentions = fields.List(fields.String())
    visible_user_ids = fields.List(fields.String(), data_key="visibleUserIds")
    file_ids = fields.List(fields.String(), data_key="fileIds")
    # files = fields.Nested(...  # TODO: TBD
    tags = fields.List(fields.String())
    # poll = fields.Nested(...  # TODO: TBD
    channel_id = fields.String(allow_none=True, data_key="channelId")
    # channel = fields.Nested(...  # TODO: TBD
    local_only = fields.Boolean(data_key="localOnly")
    reaction_acceptance = fields.Enum(
        MisskeyReactionAcceptanceEnum,
        required=True, data_key="reactionAcceptance", allow_none=True)
    # reactions = fields.Nested(...  # TODO: TBD
    renote_count = fields.Integer(required=True, data_key="renoteCount")
    replies_count = fields.Integer(required=True, data_key="repliesCount")
    uri = fields.Url()
    url = fields.Url()
    # reaction_and_user_pair_cache = fields.List(fields.String(),
    #  data_key="reactionAddUserPairCache"  # TODO: TBD
    # my_reaction = fields.Nested(...,
    #  data_key="myReaction"  # TODO: TBD

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MisskeyNote.from_dict(data)

    class Meta:
        unknown = INCLUDE


class MisskeyCreatedNoteSchema(Schema):
    created_note = fields.Nested(
        MisskeyNoteSchema(), required=True, data_key="createdNote")

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MisskeyCreatedNote(**data)
