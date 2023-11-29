from marshmallow import Schema, fields

from misskey.enum import (
    MisskeyNoteVisibilityEnum,
    MisskeyReactionAcceptanceEnum,
)

__all__ = (
    "NotesCreatePollSchema",
    "NotesCreateSchema",
)


class NotesCreatePollSchema(Schema):
    choices = fields.List(fields.String(), required=True)
    multiple = fields.Boolean(allow_none=True)
    expires_at = fields.DateTime("iso")
    expired_after = fields.Integer()


class NotesCreateSchema(Schema):
    visibility = fields.Enum(
        MisskeyNoteVisibilityEnum,
        by_value=True,
        default=MisskeyNoteVisibilityEnum.PUBLIC)
    visible_user_ids = fields.List(fields.String(), data_key="visibleUserIds")
    cw = fields.String(allow_none=True)
    local_only = fields.Boolean(default=False, data_key="localOnly")
    reaction_acceptance = fields.Enum(
        MisskeyReactionAcceptanceEnum,
        by_value=True,
        default=MisskeyReactionAcceptanceEnum.NULL)
    no_extract_mentions = fields.Boolean(
        default=False, data_key="noExtractMentions")
    no_extract_hashtags = fields.Boolean(
        default=False, data_key="noExtractHashtags")
    no_extract_emojis = fields.Boolean(
        default=False, data_key="noExtractEmojis")
    reply_id = fields.String(
        allow_none=True, default=None, data_key="replyId")
    renote_id = fields.String(
        allow_none=True, default=None, data_key="renoteId")
    channel_id = fields.String(
        allow_none=True, default=None, data_key="channelId")
    text = fields.String(allow_none=True)
    file_ids = fields.List(fields.String(), data_key="fileIds")
    media_ids = fields.List(fields.String(), data_key="mediaIds")
    poll = fields.Nested(NotesCreatePollSchema(), allow_none=True)
