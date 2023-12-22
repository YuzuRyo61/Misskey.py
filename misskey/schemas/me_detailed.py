import datetime
import inspect
from dataclasses import dataclass, field as dc_field
from typing import Optional, List

from marshmallow import Schema, fields, post_load, INCLUDE

from misskey.enum import (
    OnlineStatusEnum,
    FFVisibilityEnum,
    TwoFactorBackupCodesStockEnum,
)
from .role import (
    Role,
    RoleSchema,
)

__all__ = (
    "MeDetailed",
    "MeDetailedSchema",
)


@dataclass
class MeDetailed:
    id: str
    username: str
    online_status: OnlineStatusEnum
    created_at: datetime.datetime
    last_fetched_at: datetime.datetime
    is_locked: bool
    is_silenced: bool
    is_suspended: bool
    followers_count: int
    following_count: int
    notes_count: int
    public_reactions: bool
    ff_visibility: OnlineStatusEnum
    is_moderator: bool
    is_admin: bool
    inject_featured_note: bool
    receive_announcement_email: bool
    always_mark_nsfw: bool
    auto_sensitive: bool
    careful_bot: bool
    auto_accept_followed: bool
    no_crawle: bool
    prevent_ai_learning: bool
    is_explorable: bool
    is_deleted: bool
    hide_online_status: bool
    has_unread_specified_notes: bool
    has_unread_mentions: bool
    has_unread_announcement: bool
    has_unread_antenna: bool
    has_unread_channel: bool
    has_unread_notification: bool
    has_pending_received_follow_request: bool
    unread_notifications_count: bool
    logged_in_days: int
    host: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_blurhash: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    is_bot: bool = False
    is_cat: bool = False
    url: Optional[str] = None
    uri: Optional[str] = None
    moved_to: Optional[str] = None
    banner_url: Optional[str] = None
    banner_blurhash: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    birthday: Optional[str] = None
    lang: Optional[str] = None
    pinned_page_id: Optional[str] = None
    two_factor_enabled: bool = False
    use_password_less_login: bool = False
    security_keys: bool = False
    memo: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    roles: List[Role] = dc_field(default_factory=list)
    # noinspection SpellCheckingInspection
    notification_recieve_config: dict = dc_field(default_factory=dict)
    # TODO: Add other MeDetailed properties as well
    _extra: dict = dc_field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        payload = {
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        }
        payload["_extra"] = {
            k: v for k, v in data.items()
            if k not in inspect.signature(cls).parameters
        }
        return cls(**payload)


class MeDetailedSchema(Schema):
    id = fields.String(required=True)
    username = fields.String(required=True)
    host = fields.String(allow_none=True)
    name = fields.String(allow_none=True)
    avatar_url = fields.String(data_key="avatarUrl")
    avatar_blurhash = fields.String(
        data_key="avatarBlurhash", required=True, allow_none=True)
    is_bot = fields.Boolean(data_key="isBot")
    is_cat = fields.Boolean(data_key="isCat")
    online_status = fields.Enum(
        OnlineStatusEnum, data_key="onlineStatus",
        by_value=True)
    url = fields.Url(allow_none=True)
    uri = fields.Url(allow_none=True)
    moved_to = fields.String(allow_none=True)
    also_known_as = fields.String(allow_none=True)
    created_at = fields.DateTime("iso", data_key="createdAt", required=True)
    updated_at = fields.DateTime(
        "iso", data_key="updatedAt", required=True, allow_none=True)
    last_fetched_at = fields.DateTime(
        "iso", data_key="lastFetchedAt", allow_none=True)
    banner_url = fields.Url(
        data_key="bannerUrl", required=True, allow_none=True)
    banner_blurhash = fields.String(
        required=True, data_key="bannerBlurhash", allow_none=True)
    is_locked = fields.Boolean(data_key="isLocked", required=True)
    is_silenced = fields.Boolean(data_key="isSilenced", required=True)
    description = fields.String(required=True, allow_none=True)
    location = fields.String(
        required=True, allow_none=True)
    birthday = fields.Date(
        required=True, allow_none=True)
    lang = fields.String(
        required=True, allow_none=True)
    followers_count = fields.Integer(data_key="followersCount")
    following_count = fields.Integer(data_key="followingCount")
    notes_count = fields.Integer(data_key="notesCount")
    pinned_page_id = fields.String(
        data_key="pinnedPageId", required=True, allow_none=True)
    public_reactions = fields.Boolean(data_key="publicReactions")
    ff_visibility = fields.Enum(
        FFVisibilityEnum, data_key="ffVisibility",
        by_value=True)
    two_factor_enabled = fields.Boolean(
        required=True, data_key="twoFactorEnabled", default=False)
    use_password_less_login = fields.Boolean(
        required=True, data_key="usePasswordLessLogin", default=False)
    security_keys = fields.Boolean(
        required=True, data_key="securityKeys", default=False)
    memo = fields.String(allow_none=True)
    email = fields.String(allow_none=True)
    email_verified = fields.String(
        data_key="emailVerified", allow_none=True)
    roles = fields.List(fields.Nested(RoleSchema()))
    # noinspection SpellCheckingInspection
    notification_recieve_config = fields.Dict(
        required=True,
        data_key="notificationRecieveConfig")
    two_factor_backup_codes_stock = fields.Enum(
        TwoFactorBackupCodesStockEnum,
        data_key="twoFactorBackupCodesStock",
        required=True, by_value=True)
    is_explorable = fields.Boolean(data_key="isExplorable", required=True)
    is_suspended = fields.Boolean(data_key="isSuspended", required=True)
    is_moderator = fields.Boolean(data_key="isModerator", required=True)
    is_admin = fields.Boolean(data_key="isAdmin", required=True)
    inject_featured_note = fields.Boolean(
        data_key="injectFeaturedNote", required=True)
    receive_announcement_email = fields.Boolean(
        data_key="receiveAnnouncementEmail", required=True)
    always_mark_nsfw = fields.Boolean(data_key="alwaysMarkNsfw", required=True)
    auto_sensitive = fields.Boolean(data_key="autoSensitive", required=True)
    careful_bot = fields.Boolean(data_key="carefulBot", required=True)
    auto_accept_followed = fields.Boolean(
        data_key="autoAcceptFollowed", required=True)
    no_crawle = fields.Boolean(data_key="noCrawle", required=True)
    prevent_ai_learning = fields.Boolean(
        data_key="preventAiLearning", required=True)
    is_deleted = fields.Boolean(
        data_key="isDeleted", required=True)
    hide_online_status = fields.Boolean(
        data_key="hideOnlineStatus", required=True)
    has_unread_specified_notes = fields.Boolean(
        data_key="hasUnreadSpecifiedNotes", required=True)
    has_unread_mentions = fields.Boolean(
        data_key="hasUnreadMentions", required=True)
    has_unread_announcement = fields.Boolean(
        data_key="hasUnreadAnnouncement", required=True)
    has_unread_antenna = fields.Boolean(
        data_key="hasUnreadAntenna", required=True)
    has_unread_channel = fields.Boolean(
        data_key="hasUnreadChannel", required=True)
    has_unread_notification = fields.Boolean(
        data_key="hasUnreadNotification", required=True)
    has_pending_received_follow_request = fields.Boolean(
        data_key="hasPendingReceivedFollowRequest", required=True)
    unread_notifications_count = fields.Integer(
        data_key="unreadNotificationsCount", required=True)
    logged_in_days = fields.Integer(data_key="loggedInDays", required=True)
    # TODO: Add other MeDetailed properties as well

    # noinspection PyUnusedLocal
    @post_load()
    def load_schema(self, data, **kwargs):
        return MeDetailed.from_dict(data)

    class Meta:
        unknown = INCLUDE
