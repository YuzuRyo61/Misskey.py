import datetime
import math
import re
from enum import Enum
from typing import (
    Optional,
    Union,
    List,
    Tuple,
    Set,
    Any,
    IO as IOTypes,
    Iterable,
)
from urllib.parse import urlparse

import requests

from .enum import (
    NoteVisibility,
    FfVisibility,
    NotificationsType,
    EmailNotificationsType,
    LangType,
    WebhookEventType,
    AntennaSource,
    ChartSpan,
    HashtagsListSortKey,
    UserSortKey,
    UserOrigin,
)
from .exceptions import (
    MisskeyAuthorizeFailedException,
    MisskeyAPIException,
)


class Misskey:
    """Misskey API client class.

    Args:
        address (str): Instance address.
        You can also include the URL protocol.
        If not specified, it will be automatically
        recognized as :code:`https`.

        i (:obj:`str`, optional): Misskey API token.
        If you have an API token, you can assign it at instantiation.

        session (:obj:`requests.Session`, optional): If you have prepared the
        :obj:`requests.Session` class yourself, you can assign it here.
        Normally you do not need to specify it.

    Raises:
        MisskeyAuthorizeFailedException: Raises if token validation fails
        during instantiation.
    """

    __DEFAULT_ADDRESS: str = 'https://misskey.io'

    __address: str
    __scheme: str
    __session: requests.Session

    __token: Optional[str] = None

    timeout: Optional[Any] = 15.0
    """
    Specifies the number of seconds for HTTP communication timeout.
    Comply with "`requests <https://docs.python-requests.org/en/latest/>`_".
    """

    @property
    def address(self):
        """Misskey instance address. Cannot be edited.
        """
        return self.__address

    @property
    def __api_url(self):
        return f'{self.__scheme}://{self.__address}/api'

    @property
    def token(self) -> Optional[str]:
        """Get a token.

        When you assign a new token, it automatically verifies whether
        the token can be used.
        If validation fails, the exception
        :obj:`MisskeyAuthorizeFailedException` is raised.

        If using :code:`del`, :code:`token` will be :code:`None`.
        """
        return self.__token

    @token.setter
    def token(self, new_token: str):
        credential_res = self.__session.post(
            f'{self.__api_url}/i',
            json={
                'i': new_token,
            },
            allow_redirects=False,
            timeout=self.timeout
        )
        if credential_res.status_code == 403 or \
           credential_res.status_code == 401:
            raise MisskeyAuthorizeFailedException()

        self.__token = new_token
        return

    @token.deleter
    def token(self):
        self.__token = None

    def __init__(
        self,
        address: str = __DEFAULT_ADDRESS,
        i: Optional[str] = None,
        session: Optional[requests.Session] = None
    ):
        parse_res = urlparse(address)

        if parse_res.scheme == '':
            parse_res = urlparse(f'https://{address}')

        self.__address = str(parse_res.netloc)
        self.__scheme = str(parse_res.scheme)

        if session is None:
            session = requests.Session()
        self.__session = session

        body = {}
        if i is not None:
            self.__token = i
            body['i'] = i

        meta_res = self.__session.post(
            f'{self.__api_url}/meta',
            json=body,
            allow_redirects=False
        )

        if meta_res.status_code == 403 or \
           meta_res.status_code == 401:
            raise MisskeyAuthorizeFailedException()

    def __request_api(
        self,
        endpoint_name: str,
        **payload
    ) -> Union[dict, bool, List[dict]]:
        if self.__token is not None:
            payload['i'] = self.__token

        response = self.__session.post(
            f'{self.__api_url}/{endpoint_name}',
            json=payload,
            allow_redirects=False,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise MisskeyAPIException(response.json())

        if response.status_code == 204:
            return True
        else:
            return response.json()

    @staticmethod
    def __params(
        params: dict,
        exclude_keys: Union[
            Set[str],
            Tuple[str],
            List[str],
            None
        ] = None,
        custom_rename: Optional[dict] = None,
    ) -> dict:
        if exclude_keys is None:
            exclude_keys = tuple()

        if 'self' in params:
            del params['self']

        param_keys = list(params.keys())
        for key in param_keys:
            if params[key] is None or key in exclude_keys:
                del params[key]

        param_camel = {}
        for key, val in params.items():
            if isinstance(val, Enum):
                val = val.value
            if type(val) is set:
                val = list(val)
            if type(val) is list:
                for index, val_list in enumerate(val):
                    if isinstance(val_list, Enum):
                        val[index] = val_list.value

            if type(custom_rename) is dict and key in custom_rename.keys():
                rename_to = custom_rename[key]
                param_camel[rename_to] = val
            else:
                key_camel = re.sub(r'_(.)', lambda x: x.group(1).upper(), key)
                param_camel[key_camel] = val

        return param_camel

    def i(self) -> dict:
        """Get your credentials.

        Endpoint:
            :code:`i`

        Returns:
            dict: A dict containing your profile information will be returned.

        Note:
            :code:`token` must be set in the instance.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i')

    def meta(
        self,
        detail: bool = True,
    ) -> dict:
        """Get instance meta.

        Args:
            detail (bool): Add the details of the instance information.

        Endpoint:
            :code:`meta`

        Returns:
            dict: A dict containing instance information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('meta', detail=detail)

    def stats(self) -> dict:
        """Get instance statuses.

        Endpoint:
            :code:`stats`

        Returns:
            dict: A dict containing the number of users, the number of notes,
            etc. is returned.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('stats')

    def announcements(
        self,
        limit: int = 10,
        with_unreads: bool = True,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get announcements.

        Endpoint:
            :code:`announcements`

        Returns:
            `list` of `dict`: List of announcements.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('announcements', **params)

    def emojis(self) -> dict:
        """Get all emojis available for the instance.

        Endpoint:
            :code:`emojis`

        Returns:
            dict: Returns a list of emojis.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('emojis')

    def endpoint(
        self,
        endpoint: str,
    ) -> Union[dict, bool]:
        """Get params of the specified endpoint.

        Args:
            endpoint (str): Specifies the endpoint.

        Endpoint:
            :code:`endpoint`

        Returns:
            dict or bool: Returns the list of param names and types. If the
            endpoint is not available for the instance, returns :code:`True`.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('endpoint', endpoint=endpoint)

    def endpoints(self) -> List[str]:
        """Get all endpoints available for the instance.

        Endpoint:
            :code:`endpoints`

        Returns:
            `list` of `str`: Returns the list of endpoints.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('endpoints')

    def fetch_rss(
        self,
        url: str,
    ) -> dict:
        """Fetch RSS from the URL.

        Args:
            url (str): Specifies the URL to fetch RSS from.

        Endpoint:
            :code:`fetch-rss`

        Returns:
            dict: Returns the parsed RSS feed.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('fetch-rss', url=url)

    def get_online_users_count(self) -> dict:
        """Get number of users currently online in the instance.

        Endpoint:
            :code:`get-online-users-count`

        Returns:
            dict: Returns the online users count.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('get-online-users-count')

    def ping(self) -> dict:
        """Send a ping.

        Endpoint:
            :code:`ping`

        Returns:
            dict: Returns response time in epoch milliseconds.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('ping')

    def server_info(self) -> dict:
        """Get information of the server machine that runs the instance.

        Endpoint:
            :code:`server-info`

        Returns:
            dict: Returns the server machine information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('server-info')

    def i_favorites(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get your favorites.

        Args:
            limit (int): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (:obj:`str`, optional): Specify the first ID to get.

            until_id (:obj:`str`, optional): Specify the last ID to get.

        Endpoint:
            :code:`i/favorites`

        Note:
            :code:`token` must be set in the instance.

        Returns:
            `list` of `dict`: List of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        param = self.__params(locals())

        return self.__request_api('i/favorites', **param)

    def i_pin(
        self,
        note_id: str,
    ) -> dict:
        """Pin a note.

        Args:
            note_id (str): Note id.

        Endpoint:
            :code:`i/pin`

        Note:
            :code:`token` must be set in the instance.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/pin', noteId=note_id)

    def i_unpin(
        self,
        note_id: str,
    ) -> dict:
        """Unpin a note.

        Args:
            note_id (str): Note id.

        Endpoint:
            :code:`i/unpin`

        Note:
            :code:`token` must be set in the instance.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/unpin', noteId=note_id)

    def i_notifications(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        following: bool = False,
        unread_only: bool = False,
        mark_as_read: bool = True,
        include_types: Union[
            List[Union[NotificationsType, str]],
            Tuple[NotificationsType],
            Set[NotificationsType],
            None,
        ] = None,
        exclude_types: Union[
            List[Union[NotificationsType, str]],
            Tuple[NotificationsType],
            Set[NotificationsType],
            None,
        ] = None,
    ) -> List[dict]:
        """Get your notifications.

        Args:
            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (:obj:`str`, optional): Specify the first ID to get.

            until_id (:obj:`str`, optional): Specify the last ID to get.

            following (bool): Only following.

            unread_only (bool): Get only unread notifications.

            mark_as_read (bool): Specify whether to mark it as read
            when it is acquired.

            include_types (:obj:`list`, :obj:`tuple` or :obj:`set`): Specifies
            the type of notification to include.

            exclude_types (:obj:`list`, :obj:`tuple` or :obj:`set`): Specifies
            the type of notification to exclude.

        Endpoint:
            :code:`i/notifications`

        Note:
            :code:`token` must be set in the instance.

        Returns:
            `list` of `dict`: List of notifications.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if type(include_types) is list:
            for index, val in enumerate(include_types):
                if type(val) is str:
                    include_types[index] = NotificationsType(val)

        if type(exclude_types) is list:
            for index, val in enumerate(exclude_types):
                if type(val) is str:
                    exclude_types[index] = NotificationsType(val)

        params = self.__params(locals())
        return self.__request_api('i/notifications', **params)

    def notifications_mark_all_as_read(self) -> bool:
        """Mark all as read to your notifications.

        Endpoint:
            :code:`notifications/mark-all-as-read`

        Note:
            :code:`token` must be set in the instance.

        Returns:
            bool: Returns :code:`True` if successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

        """
        return self.__request_api(
            'notifications/mark-all-as-read'
        )

    def i_update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        lang: Union[LangType, str, None] = None,
        location: Optional[str] = None,
        birthday: Union[
            datetime.date,
            datetime.datetime,
            str,
            None,
        ] = None,
        avatar_id: Optional[str] = None,
        banner_id: Optional[str] = None,
        fields: Union[List[dict], dict, None] = None,
        is_locked: Optional[bool] = None,
        is_explorable: Optional[bool] = None,
        hide_online_status: Optional[bool] = None,
        public_reactions: Optional[bool] = None,
        careful_bot: Optional[bool] = None,
        auto_accept_followed: Optional[bool] = None,
        no_crawle: Optional[bool] = None,
        is_bot: Optional[bool] = None,
        is_cat: Optional[bool] = None,
        show_timeline_replies: Optional[bool] = None,
        inject_featured_note: Optional[bool] = None,
        receive_announcement_email: Optional[bool] = None,
        always_mark_nsfw: Optional[bool] = None,
        auto_sensitive: Optional[bool] = None,
        ff_visibility: Union[FfVisibility, str, None] = None,
        pinned_page_id: Optional[str] = None,
        muted_words: Optional[List[List[str]]] = None,
        muted_instances: Optional[List[str]] = None,
        muting_notification_types: Optional[
            Iterable[Union[NotificationsType, str]]
        ] = None,
        email_notification_types: Optional[
            Iterable[Union[EmailNotificationsType, str]]
        ] = None,
    ) -> dict:
        """Update your profiles.

        Args:
            name (:obj:`str`, optional): Your name to display.

            description (:obj:`str`, optional): Write an introductory text.

            lang (:obj:`str`, optional): Specify your language.

            location (:obj:`str`, optional): Specify your location.

            birthday (:obj:`datetime.date`,
            :obj:`datetime.datetime` or :obj:`str`, optional):
            Specify your birthday date.

            avatar_id (:obj:`str`, optional): Avatar's drive id.

            banner_id (:obj:`str`, optional): Banner's drive id.

            fields (:obj:`list` of :obj:`dict` or :obj:`dict`, optional):
            Profile supplementary information.

            is_locked (:obj:`bool`, optional): Whether to make
            follow-up approval system.

            is_explorable (:obj:`bool`, optional): Whether to set as
            a discoverable user.

            hide_online_status (:obj:`bool`, optional): Whether to
            hide online status.

            public_reactions (:obj:`bool`, optional): Whether to make your
            reactions publicly visible.

            careful_bot (:obj:`bool`, optional): Whether to
            approve follow-ups from bots.

            auto_accept_followed (:obj:`bool`, optional): Whether to
            automatically follow from the users you are following

            no_crawle (:obj:`bool`, optional): Specifies whether to
            prevent it from being tracked by search engines.

            is_bot (:obj:`bool`, optional): Whether to operate as a bot.

            is_cat (:obj:`bool`, optional): Specifies whether to use nyaise.

            show_timeline_replies (:obj:`bool`, optional): Specifies whether to
            show replies to other users in the timeline.

            inject_featured_note (:obj:`bool`, optional): Specifies whether to
            show featured notes in the timeline.

            receive_announcement_email (:obj:`bool`, optional): Specifies
            whether to receive email notification from the instance.

            always_mark_nsfw (:obj:`bool`, optional): Whether to give NSFW
            to the posted file by default.

            auto_sensitive (:obj:`bool`, optional): Specifies whether to allow
            automatic detection and marking of NSFW media.

            ff_visibility (:obj:`str`, optional): Specifies visibility of
            follows and followers. Available values are enumerated in
            :class:`enum.FfVisibility`.

            pinned_page_id (:obj:`str`, optional): ID of the page to be fixed.

            muted_words (:obj:`list` of :obj:`list` of :obj:`str`, optional):
            Word to mute.

            muted_instance (:obj:`list` of :obj:`str`, optional): Specifies
            instances to mute.

            muting_notification_types (:obj:`list` of :obj:`str`, optional):
            Notification type to hide. Available values are enumerated in
            :class:`enum.NotificationsType`.

            email_notification_types (:obj:`list` of :obj:`str`, optional):
            Specify the notification type for email notification. Available
            values are enumerated in :class:`enum.EmailNotificationsType`.

        Endpoint:
            :code:`i/update`

        Note:
            :code:`token` must be set in the instance.

        Returns:
            bool: Returns :code:`True` if successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

        """
        if type(lang) is str:
            lang = LangType(lang)

        if isinstance(birthday, datetime.date) or \
           isinstance(birthday, datetime.datetime):
            birthday = birthday.strftime('%Y-%m-%d')

        if issubclass(type(fields), dict):
            fields = [{'name': key, 'value': val}
                      for key, val in fields.items()]

        if type(ff_visibility) is str:
            ff_visibility = FfVisibility(ff_visibility)

        if muting_notification_types is not None:
            muting_notification_types = [
                NotificationsType(val) if type(val) is str else val
                for val in muting_notification_types
            ]

        if email_notification_types is not None:
            email_notification_types = [
                EmailNotificationsType(val) if type(val) is str else val
                for val in email_notification_types
            ]

        params = self.__params(locals())
        return self.__request_api('i/update', **params)

    def i_export_blocking(self) -> bool:
        """Export list of users you are blocking to your drive.

        Endpoint:
            :code:`i/export-blocking`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/export-blocking')

    def i_export_favorites(self) -> bool:
        """Export list of favorite notes to your drive.

        Endpoint:
            :code:`i/export-favorites`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/export-favorites')

    def i_export_following(
        self,
        exclude_muting: bool = False,
        exclude_inactive: bool = False,
    ) -> bool:
        """Export list of users you are following to your drive.

        Args:
            exclude_muting (bool, default: :code:`False`): Specifies whether to
            exclude users you are muting.

            exclude_inactive (bool, default: :code:`False`): Specifies whether
            to exclude users that are inactive for more than 90 days.

        Endpoint:
            :code:`i/export-following`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/export-following', **params)

    def i_export_mute(self) -> bool:
        """Export list of users you are muting to your drive.

        Endpoint:
            :code:`i/export-mute`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/export-mute')

    def i_export_notes(self) -> bool:
        """Export list of notes you have created to your drive.

        Endpoint:
            :code:`i/export-notes`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/export-notes')

    def i_export_user_lists(self) -> bool:
        """Export list of user lists you have created to your drive.

        Endpoint:
            :code:`i/export-user-lists`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/export-user-lists')

    def i_gallery_likes(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of likes you gave to gallery posts.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`i/gallery/likes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of likes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/gallery/likes', **params)

    def i_gallery_posts(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of gallery posts you have created.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`i/gallery/posts`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of gallery posts.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/gallery/posts', **params)

    def i_get_word_muted_notes_count(self) -> dict:
        """Get number of notes that were word-muted by your preferences.

        Endpoint:
            :code:`i/get-word-muted-notes-count`

        Returns:
            dict: Returns word muted notes count.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/get-word-muted-notes-count')

    def i_import_blocking(
        self,
        file_id: str,
    ) -> bool:
        """Import users to block from your drive file.

        Args:
            file_id (str): Specifies the file ID to import.

        Endpoint:
            :code:`i/import-blocking`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/import-blocking', fileId=file_id)

    def i_import_following(
        self,
        file_id: str,
    ) -> bool:
        """Import users to follow from your drive file.

        Args:
            file_id (str): Specifies the file ID to import.

        Endpoint:
            :code:`i/import-following`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/import-following', fileId=file_id)

    def i_import_muting(
        self,
        file_id: str,
    ) -> bool:
        """Import users to mute from your drive file.

        Args:
            file_id (str): Specifies the file ID to import.

        Endpoint:
            :code:`i/import-muting`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/import-muting', fileId=file_id)

    def i_import_user_lists(
        self,
        file_id: str,
    ) -> bool:
        """Import user lists from your drive file.

        Args:
            file_id (str): Specifies the file ID to import.

        Endpoint:
            :code:`i/import-user-lists`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/import-user-lists', fileId=file_id)

    def i_page_likes(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of likes you gave to pages.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`i/page-likes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of likes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/page-likes', **params)

    def i_pages(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of pages you have created.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`i/pages`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of likes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/pages', **params)

    def i_read_all_unread_notes(self) -> bool:
        """Mark all unread notes as read.

        Endpoint:
            :code:`i/read-all-unread-notes`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/read-all-unread-notes')

    def i_read_announcement(
        self,
        announcement_id: str,
    ) -> bool:
        """Mark the specified annoucement as read.

        Args:
            announcement_id (str): Specifies the announcement ID to read.

        Endpoint:
            :code:`i/read-announcement`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'i/read-announcement',
            announcementId=announcement_id,
        )

    def i_webhooks_create(
        self,
        name: str,
        url: str,
        secret: str,
        on: List[Union[WebhookEventType, str]],
    ) -> dict:
        """Create a webhook.

        Args:
            name (str): Specifies the name of webhook.

            url (str): Specifies the URL to send HTTP request to.

            secret (str): Specifies the secret value.

            on (str): Specifies the list of events. Available values are
            enumerated in :class:`enum.WebhookEventType`.

        Endpoint:
            :code:`i/webhooks/create`

        Returns:
            dict: Returns the created webhook information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        on = [
            WebhookEventType(val) if type(val) is str else val
            for val in on
        ]
        params = self.__params(locals())
        return self.__request_api('i/webhooks/create', **params)

    def i_webhooks_delete(
        self,
        webhook_id: str,
    ) -> bool:
        """Delete a webhook.

        Args:
            webhook_id (str): Specifies the webhook ID to delete.

        Endpoint:
            :code:`i/webhooks/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('i/webhooks/delete', webhookId=webhook_id)

    def i_webhooks_list(self) -> List[dict]:
        """Get list of webhooks you have created.

        Endpoint:
            :code:`i/webhooks/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of webhooks.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/webhooks/list', **params)

    def i_webhooks_show(
        self,
        webhook_id: str,
    ) -> dict:
        """Get information of the specified webhook.

        Args:
            webhook_id (str): Specifies the webhook ID to get.

        Endpoint:
            :code:`i/webhooks/show`

        Returns:
            dict: Returns the webhook information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('i/webhooks/show', **params)

    def i_webhooks_update(
        self,
        webhook_id: str,
        name: str,
        url: str,
        secret: str,
        on: List[Union[WebhookEventType, str]],
        active: bool,
    ) -> bool:
        """Update a webhook.

        Args:
            webhook_id (str): Specifies the webhook ID to update.

            name (str): Specifies the name of webhook.

            url (str): Specifies the URL to send HTTP request to.

            secret (str): Specifies the secret value.

            on (str): Specifies the list of events. Available values are
            enumerated in :class:`enum.WebhookEventType`.

            active (bool): Specifies whether to activate the webhook.

        Endpoint:
            :code:`i/webhooks/update`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`on` is invalid.
        """
        on = [
            WebhookEventType(val) if type(val) is str else val
            for val in on
        ]
        params = self.__params(locals())
        return self.__request_api('i/webhooks/update', **params)

    def notifications_create(
        self,
        body: str,
        header: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> bool:
        """Create a notification.

        Args:
            body (str): Specifies the body text of the notification.

            header (str): Specifies the header text of the notification.

            icon (str): Specifies the URL of the notification icon image.

        Endpoint:
            :code:`notifications/create`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notifications/create', **params)

    def notifications_read(
        self,
        notification_id: Union[str, List[str]],
    ) -> bool:
        """Mark a notification as read.

        Args:
            notification_id (str or :obj:`list` of :obj:`str`): Specifies
            notification ID to mark as read. If specified by :obj:`list`,
            read multiple notifications.

        Endpoint:
            :code:`notifications/read`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if type(notification_id) is str:
            notification_id = [notification_id]
        return self.__request_api(
            'notifications/read',
            notificationIds=notification_id
        )

    def notes_create(
        self,
        text: Optional[str] = None,
        cw: Optional[str] = None,
        visibility: Union[NoteVisibility, str] = NoteVisibility.PUBLIC,
        visible_user_ids: Optional[List[str]] = None,
        local_only: bool = False,
        no_extract_mentions: bool = False,
        no_extract_hashtags: bool = False,
        no_extract_emojis: bool = False,
        file_ids: Optional[List[str]] = None,
        reply_id: Optional[str] = None,
        renote_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        poll_choices: Optional[Union[List[str], Tuple[str]]] = None,
        poll_multiple: bool = False,
        poll_expires_at: Optional[Union[int, datetime.datetime]] = None,
        poll_expired_after: Optional[Union[int, datetime.timedelta]] = None,
    ) -> dict:
        """Create a note.

        Args:
            text (:obj:`str`, optional): Specify the text.

            cw (:obj:`str`, optional): Specify the CW(Content Warning).

            visibility (:obj:`str`, default: :code:`public`): Post range.
            Specifies the enumeration in :obj:`NoteVisibility`.

            visible_user_ids (:obj:`list` of :obj:`str`, optional):
            If :code:`visibility` is :code:`specified`,
            specify the user ID in the list.

            local_only (:obj:`bool`, optional): Specifies whether to
            post only the instance you are using.

            no_extract_mentions (:obj:`bool`, optional): Specifies whether
            to detect mentions from the text.

            no_extract_hashtags (:obj:`bool`, optional): Specifies whether
            to detect hashtags from the text.

            no_extract_emojis (:obj:`bool`, optional): Specifies whether
            to detect emojis from the text.

            file_ids (:obj:`list` of :obj:`str`, optional): Specify
            the file ID to attach in the list.

            reply_id (:obj:`str`, optional): Specify the Note ID of
            the reply destination.

            renote_id (:obj:`str`, optional): Specify the Note ID to renote.

            channel_id (:obj:`str`, optional): Specify the channel ID to post
            the note to.

            poll_choices (:obj:`list` of :obj:`str`, optional): Specify the
            voting item. You can specify 2 or more and 10 or less.

            poll_multiple (:obj:`bool`, optional): Specifies whether
            to allow multiple votes. This is valid only when
            :code:`poll_choices` is specified.

            poll_expires_at (:obj:`datetime.datetime`, optional): Specify
            the expiration date of the vote. If not specified,
            it will be indefinite. Cannot be used
            with :code:`poll_expired_after`.

            poll_expired_after (:obj:`datetime.timedelta`, optional): Specifies
            the validity period of the vote. If not specified, it will
            be indefinite. Cannot be used with :code:`poll_expired_at`.

        Endpoint:
            :code:`notes/create`

        Note:
            :code:`token` must be set in the instance.

            You must specify at least either :code:`text` or :code:`files_id`.

        Returns:
            dict: The dict of the posted result is returned.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if type(visibility) is str:
            visibility = NoteVisibility(visibility)

        if (type(poll_choices) == list or type(poll_choices) == tuple) and \
           10 >= len(poll_choices) >= 2:
            if isinstance(poll_expires_at, datetime.datetime):
                poll_expires_at = math.floor(
                    poll_expires_at.timestamp() * 1000)
            if isinstance(poll_expired_after, datetime.timedelta):
                poll_expired_after = poll_expired_after.seconds * 1000

            poll = {
                'choices': poll_choices,
                'expiresAt': poll_expires_at,
                'expiredAfter': poll_expired_after,
            }

        params = self.__params(
            locals(),
            {
                'poll_choices',
                'poll_multiple',
                'poll_expires_at',
                'poll_expired_after'
            }
        )

        return self.__request_api('notes/create', **params)

    def notes_show(
        self,
        note_id: str,
    ) -> dict:
        """Show a note.

        Args:
            note_id (str): Specify the Note ID to get.

        Endpoint:
            :code:`notes/show`

        Returns:
            dict: A dict with the specified Note ID is returned.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('notes/show', noteId=note_id)

    def notes_conversation(
        self,
        note_id: str,
        limit: int = 10,
        offset: Optional[int] = None,
    ) -> List[dict]:
        """Show note conversations.

        Args:
            note_id (str): Specify the Note ID to get.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`notes/conversation`

        Returns:
            :obj:`list` of :obj:`dict`: Gets the Note associated
            with that Note.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/conversation', **params)

    def notes_children(
        self,
        note_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Show note children.

        Args:
            note_id (str): Specify the Note ID to get.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

        Endpoint:
            :code:`notes/children`

        Returns:
            :obj:`list` of :obj:`dict`: Gets the Note associated
            with that Note.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/children', **params)

    def notes_replies(
        self,
        note_id: str,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Show note replies.

        Args:
            note_id (str): Specify the Note ID to get.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

        Endpoint:
            :code:`notes/replies`

        Returns:
            :obj:`list` of :obj:`dict`: Gets the Note associated
            with that Note.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/replies', **params)

    def notes_renotes(
        self,
        note_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Show renotes.

        Args:
            note_id (str): Specify the Note ID to get.

            limit(int, optional): Specify the amount to get.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

        Endpoint:
            :code:`notes/renotes`

        Returns:
            :obj:`list` of :obj:`dict`: Gets the Note associated
            with that Note.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/renotes', **params)

    def notes_unrenote(
        self,
        note_id: str
    ) -> bool:
        """Unrenote a note.

        Args:
            note_id (str): Specify the Note ID to unrenote.

        Endpoint:
            :code:`notes/unrenote`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('notes/unrenote', noteId=note_id)

    def notes_reactions(
        self,
        note_id: str,
        reaction_type: Optional[str] = None,
        limit: int = 10,
        offset: Optional[int] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Show note reactions.

        Args:
            note_id (str): Specify the Note ID to get.

            reaction_type (str, optional): Specify the reaction type to get.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            offset (int, optional): Specifies the offset to get.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

        Endpoint:
            :code:`notes/reactions`

        Returns:
            :obj:`list` of :obj:`dict`: Get reactions in associated note.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(
            locals(),
            custom_rename={
                'reaction_type': 'type',
            }
        )
        return self.__request_api('notes/reactions', **params)

    def notes_reactions_create(
        self,
        note_id: str,
        reaction: str,
    ) -> bool:
        """Create a reaction in a note.

        Args:
            note_id (str): Specify the Note ID to create your reaction.

            reaction (str): Specify the reaction type.

        Endpoint:
            :code:`notes/reactions/create`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/reactions/create', **params)

    def notes_reactions_delete(
        self,
        note_id: str,
    ) -> bool:
        """Delete a reaction in a note.

        Args:
            note_id (str): Specify the Note ID to delete your reaction.

        Endpoint:
            :code:`notes/reactions/delete`

        Returns:
            bool: Returns :code:`True` if the reaction was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/reactions/delete', **params)

    def notes_polls_vote(
        self,
        note_id: str,
        choice: int,
    ) -> bool:
        """Vote in a note poll.

        Args:
            note_id (str): Specify the Note ID to vote.

            choice (int): Specify the choice to vote. Specify from 0.

        Endpoint:
            :code:`notes/polls/vote`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'notes/polls/vote',
            noteId=note_id,
            choice=choice,
        )

    def notes_state(
        self,
        note_id: str,
    ) -> dict:
        """Show a state of a note.

        Args:
            note_id (str): Specify the Note ID to get.

        Endpoint:
            :code:`notes/state`

        Returns:
            :obj:`dict`: Get state of a note.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'notes/state',
            noteId=note_id,
        )

    def notes_favorites_create(
        self,
        note_id: str,
    ) -> bool:
        """Mark as favorite a note.

        Args:
            note_id (str): Specify the Note ID to make a favorite.

        Endpoint:
            :code:`notes/favorites/create`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'notes/favorites/create',
            noteId=note_id,
        )

    def notes_favorites_delete(
        self,
        note_id: str,
    ) -> bool:
        """Delete favorite a note.

        Args:
            note_id (str): Specify the Note ID to unmark a favorite.

        Endpoint:
            :code:`notes/favorites/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'notes/favorites/delete',
            noteId=note_id,
        )

    def notes_delete(
        self,
        note_id: str,
    ) -> bool:
        """Delete a note.

        Args:
            note_id (str): Specify the Note ID to delete.

        Endpoint:
            :code:`notes/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('notes/delete', noteId=note_id)

    def notes_timeline(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
        include_my_renotes: bool = True,
        include_renoted_my_notes: bool = True,
        include_local_renotes: bool = True,
        with_files: bool = False,
    ) -> List[dict]:
        """Show your home timeline.

        Args:
            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            since_date (int, datetime.datetime, optional): Specify
            the first date to get.

            until_date (int, datetime.datetime, optional): Specify
            the last date to get.

            include_my_renotes (bool, optional): Specify whether to
            include your notes.

            include_renoted_my_notes (bool, optional): Specify whether to
            include renotes of your notes.

            include_local_renotes (bool, optional): Specify whether to
            include local renotes.

            with_files (bool, optional): Specify whether to get only notes with
            files.

        Endpoint:
            :code:`notes/timeline`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(
                since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(
                until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('notes/timeline', **params)

    def notes_local_timeline(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
        with_files: bool = False,
        file_type: Optional[List[str]] = None,
        exclude_nsfw: bool = False,
    ) -> List[dict]:
        """Show local timeline.

        Args:
            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            since_date (int, datetime.datetime, optional): Specify
            the first date to get.

            until_date (int, datetime.datetime, optional): Specify
            the last date to get.

            with_files (bool, optional): Specify whether to get only notes with
            files.

            file_type (:obj:`list` of :obj:`str`, optional): Specify the file
            type to get.

            exclude_nsfw (bool, optional): Specify whether to exclude NSFW
            (Not safe for work) notes.

        Endpoint:
            :code:`notes/local-timeline`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(
                since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(
                until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('notes/local-timeline', **params)

    def notes_hybrid_timeline(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
        include_my_renotes: bool = True,
        include_renoted_my_notes: bool = True,
        include_local_renotes: bool = True,
        with_files: bool = False,
    ) -> List[dict]:
        """Show hybrid(home + local) timeline.

        Args:
            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            since_date (int, datetime.datetime, optional): Specify
            the first date to get.

            until_date (int, datetime.datetime, optional): Specify
            the last date to get.

            include_my_renotes (bool, optional): Specify whether to
            include your notes.

            include_renoted_my_notes (bool, optional): Specify whether to
            include renotes of your notes.

            include_local_renotes (bool, optional): Specify whether to
            include local renotes.

            with_files (bool, optional): Specify whether to get only notes with
            files.

        Endpoint:
            :code:`notes/hybrid-timeline`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(
                since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(
                until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('notes/hybrid-timeline', **params)

    def notes_global_timeline(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
        with_files: bool = False,
    ) -> List[dict]:
        """Show global timeline.

        Args:
            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            since_date (int, datetime.datetime, optional): Specify
            the first date to get.

            until_date (int, datetime.datetime, optional): Specify
            the last date to get.

            with_files (bool, optional): Specify whether to get only notes with
            files.

        Endpoint:
            :code:`notes/global-timeline`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(
                since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(
                until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('notes/global-timeline', **params)

    def notes(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        local: bool = False,
        reply: Optional[bool] = None,
        renote: Optional[bool] = None,
        with_files: Optional[bool] = None,
        pool: Optional[bool] = None,
    ) -> List[dict]:
        """Get a list of notes.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            local (bool, default: :code:`False`): Specifies whether to only get
            local notes.

            reply (bool, optional): Specifies whether to get replies. If
            :code:`True`, get only replies and if :code:`False`, get only
            notes which are not replies. If :code:`None`, get both notes.

            renote (bool, optional): Specifies whether to get renotes. If
            :code:`True`, get only renotes and if :code:`False`, get only
            notes which are not renotes. If :code:`None`, get both notes.

            with_files (bool, optional): Specifies whether to get note with
            files. If :code:`True`, get only notes with files and if
            :code:`False`, get only notes without files. If :code:`None`, get
            both notes.

            poll (bool, optional): Specifies whether to get note with poll. If
            :code:`True`, get only notes with polls and if :code:`False`, get
            only notes without polls. If :code:`None`, get both notes.

        Endpoint:
            :code:`notes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes', **params)

    def notes_clips(
        self,
        note_id: str
    ) -> List[dict]:
        """Get a list of clips that contain the specified note.

        Args:
            note_id (str): Specifies the note ID.

        Endpoint:
            :code:`notes/clips`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('notes/clips', noteId=note_id)

    def notes_featured(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> List[dict]:
        """Get featured notes.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            offset (int, default: 0): Specifies the offset to get.

        Endpoint:
            :code:`notes/featured`

        Returns:
            :obj:`list` of :obj:`dict`: Returns featured notes sorted in
            reverse chronological order.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/featured', **params)

    def notes_mentions(
        self,
        following: bool = False,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        visibility: Optional[Union[NoteVisibility, str]] = None,
    ) -> List[dict]:
        """Get a list of notes that mention you.

        Args:
            following (bool, default: :code:`False`): Specifies whether to get
            notes only from you or users you follow.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            visibility (str, optional): Specifies the visibility of the note to
            get. Available values are enumerated in
            :class:`enum.NoteVisibility`.

        Endpoint:
            :code:`notes/mentions`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`visibility` is invalid.
        """
        if type(visibility) is str:
            visibility = NoteVisibility(visibility)
        params = self.__params(locals())
        return self.__request_api('notes/mentions', **params)

    def notes_polls_recommendation(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> List[dict]:
        """Get a list of recommended notes with polls.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            offset (int, default: 0): Specifies the offset to get.

        Endpoint:
            :code:`notes/polls/recommendation`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of recommended notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/polls/recommendation', **params)

    def notes_search(
        self,
        query: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        offset: int = 0,
        host: Optional[str] = None,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> List[dict]:
        """Search notes that contain query.

        Args:
            query (str): Specifies search query.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            offset (int, default: 0): Specifies the offset to get.

            host (str, optional): Specifies the host to search. The local host
            is represented with :code:`None`.

            user_id (str, optional): Specifies the user ID to search.

            channel_id (str, optional): Specifies the channel ID to search.

        Endpoint:
            :code:`notes/search`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes.

        Note:
            If :code:`user_id` is set, :code:`channel_id` is ignored.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('notes/search', **params)

    def notes_search_by_tag(
        self,
        tag: Union[str, List[List[str]]],
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        reply: Optional[bool] = None,
        renote: Optional[bool] = None,
        with_files: Optional[bool] = None,
        poll: Optional[bool] = None,
    ) -> List[dict]:
        """Search notes that contain specified hashtags.

        Args:
            tag (str or :obj:`list` of :obj:`list` of :obj:`str`): Specifies
            the hashtag to search. If specified by :obj:`list`, tags inside the
            inner lists are chained with AND, and the outer lists are chained
            with OR.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            reply (bool, optional): Specifies whether to get replies. If
            :code:`True`, get only replies and if :code:`False`, get only
            notes which are not replies. If :code:`None`, get both notes.

            renote (bool, optional): Specifies whether to get renotes. If
            :code:`True`, get only renotes and if :code:`False`, get only
            notes which are not renotes. If :code:`None`, get both notes.

            with_files (bool, optional): Specifies whether to get note with
            file. If :code:`True`, get only notes with files and if
            :code:`False`, get only notes without files. If :code:`None`, get
            both notes.

            poll (bool, optional): Specifies whether to get note with poll. If
            :code:`True`, get only notes with polls and if :code:`False`, get
            only notes without polls. If :code:`None`, get both notes.

        Endpoint:
            :code:`notes/search-by-tag`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if type(tag) is list:
            query = tag
            tag = None
        params = self.__params(locals())
        return self.__request_api('notes/search-by-tag', **params)

    def notes_thread_muting_create(
        self,
        note_id: str,
    ) -> bool:
        """Mute the thread that contains the specified note.

        Args:
            note_id (str): Specifies the note ID.

        Endpoint:
            :code:`notes/thread-muting/create`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('notes/thread-muting/create', noteId=note_id)

    def notes_thread_muting_delete(
        self,
        note_id: str,
    ) -> bool:
        """Unmute the thread that contains the specified note.

        Args:
            note_id (str): Specifies the note ID.

        Endpoint:
            :code:`notes/thread-muting/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('notes/thread-muting/delete', noteId=note_id)

    def notes_user_list_timeline(
        self,
        list_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
        include_my_renotes: bool = True,
        include_renoted_my_notes: bool = True,
        include_local_renotes: bool = True,
        with_files: bool = False,
    ) -> List[dict]:
        """Show the user list timeline.

        Args:
            list_id (str): Specifies the list ID.

            limit (int, optional): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            since_date (int, datetime.datetime, optional): Specifies
            the first date to get.

            until_date (int, datetime.datetime, optional): Specifies
            the last date to get.

            include_my_renotes (bool, optional): Specifies whether to
            include your notes.

            include_renoted_my_notes (bool, optional): Specifies whether to
            include renotes of your notes.

            include_local_renotes (bool, optional): Specifies whether to
            include local renotes.

            with_files (bool, optional): Specifies whether to get only notes
            with files.

        Endpoint:
            :code:`notes/user-list-timeline`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('notes/user-list-timeline', **params)

    def users_show(
        self,
        user_id: Optional[str] = None,
        user_ids: Optional[List[str]] = None,
        username: Optional[str] = None,
        host: Optional[str] = None,
    ) -> Union[dict, List[dict]]:
        """Show user.

        Args:
            user_id (str, optional): Specify the user ID.

            user_ids (list of str, optional): Specify the user IDs.

            username (str, optional): Specify the username.

            host (str, optional): Specify the host.

        Endpoint:
            :code:`users/show`

        Note:
            You must specify one of user_id, user_ids, username (and host).

            If you specify :code:`user_ids`, it returns a list of users.

        Returns:
            :obj:`dict` or :obj:`list` of :obj:`dict`: Returns a user or
            a list of users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

        """
        params = self.__params(locals())
        return self.__request_api('users/show', **params)

    def users_following(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        host: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Get the follow list of the specified user.

        Args:
            user_id (str, optional): Specify the user ID.

            username (str, optional): Specify the username.

            host (str, optional): Specify the host.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

        Endpoint:
            :code:`users/following`

        Note:
            You must specify one of user_id, username (and host).

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        if host is None:
            params['host'] = None
        return self.__request_api('users/following', **params)

    def users_followers(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        host: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Get the follower list of the specified user.

        Args:
            user_id (str, optional): Specify the user ID.

            username (str, optional): Specify the username.

            host (str, optional): Specify the host.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

        Endpoint:
            :code:`users/followers`

        Note:
            You must specify one of user_id, username (and host).

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        if host is None:
            params['host'] = None
        return self.__request_api('users/followers', **params)

    def users_notes(
        self,
        user_id: str,
        include_replies: bool = True,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[
            datetime.datetime,
            int,
            None,
        ] = None,
        until_date: Union[
            datetime.datetime,
            int,
            None,
        ] = None,
        include_my_renotes: bool = True,
        with_files: bool = False,
        file_type: Optional[List[str]] = None,
        exclude_nsfw: bool = False,
    ) -> List[dict]:
        """Get the note list of the specified user.

        Args:
            user_id (str): Specify the user ID.

            include_replies (bool, optional): Specify whether to
            include replies.

            limit (int, optional): Specify the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            since_date (:obj:`datetime.datetime`, optional): Specify the
            first date to get.

            until_date (:obj:`datetime.datetime`, optional): Specify the
            last date to get.

            include_my_renotes (bool, optional): Specify whether to
            include my renotes.

            with_files (bool, optional): Specify whether to include
            files.

            file_type (:obj:`list` of :obj:`str`, optional): Specify
            the file type to get.

            exclude_nsfw (bool, optional): Specify whether to exclude
            NSFW notes.

        Endpoint:
            :code:`users/notes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(until_date.timestamp() * 1000)

        params = self.__params(locals())
        return self.__request_api('users/notes', **params)

    def users_stats(
        self,
        user_id: str,
    ) -> dict:
        """Gets the count for the specified user

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`users/stats`

        Returns:
            :obj:`dict`: Returns a count for the specified user.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('users/stats', userId=user_id)

    def users_relation(
        self,
        user_id: Union[str, List[str]],
    ) -> Union[dict, List[dict]]:
        """Get the relation of the specified user(s).

        Args:
            user_id (:obj:`str` or :obj:`list` of :obj:`str`): Specify the
            user ID(s).

        Endpoint:
            :code:`users/relation`

        Note:
            If :code:`user_id` is specified by str, it will be returned
            by dict.

            If :code:`user_id` is specified by list, it will be returned
            by dict of list.

        Returns:
            :obj:`dict` or :obj:`list` of :obj:`dict`: Returns the relation.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('users/relation', userId=user_id)

    def users_lists_create(
        self,
        name: str,
    ) -> dict:
        """Create user list.

        Args:
            name (str): Specify the list name.

        Endpoint:
            :code:`users/lists/create`

        Returns:
            dict: Returns the new list information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('users/lists/create', name=name)

    def users_lists_list(self) -> List[dict]:
        """Get user list.

        Endpoint:
            :code:`users/lists/list`

        Returns:
            list of dict: Returns a list of user lists.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('users/lists/list')

    def users_lists_show(
        self,
        list_id: str,
    ) -> dict:
        """Get user list detail.

        Args:
            list_id (str): Specify the list ID.

        Endpoint:
            :code:`users/lists/show`

        Returns:
            dict: Returns the list information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('users/lists/show', listId=list_id)

    def users_lists_push(
        self,
        list_id: str,
        user_id: str,
    ) -> bool:
        """Add user to user list.

        Args:
            list_id (str): Specify the list ID.

            user_id (str): Specify the user ID.

        Endpoint:
            :code:`users/lists/push`

        Returns:
            bool: Returns :code:`True` if the user is added to
            the list.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/lists/push', **params)

    def users_lists_pull(
        self,
        list_id: str,
        user_id: str,
    ) -> bool:
        """Remove user from user list.

        Args:
            list_id (str): Specify the list ID.

            user_id (str): Specify the user ID.

        Endpoint:
            :code:`users/lists/pull`

        Returns:
            bool: Returns :code:`True` if the user is removed from
            the list.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/lists/pull', **params)

    def users_lists_update(
        self,
        list_id: str,
        name: str,
    ) -> dict:
        """Update user list.

        Args:
            list_id (str): Specify the list ID.

            name (str): Specify the new list name.

        Endpoint:
            :code:`users/lists/update`

        Returns:
            dict: Returns the updated list information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/lists/update', **params)

    def users_lists_delete(
        self,
        list_id: str,
    ) -> bool:
        """Delete user list.

        Args:
            list_id (str): Specify the list ID.

        Endpoint:
            :code:`users/lists/delete`

        Returns:
            bool: Returns :code:`True` if the list is deleted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('users/lists/delete', listId=list_id)

    def users_report_abuse(
        self,
        user_id: str,
        comment: str,
    ) -> bool:
        """Report abuse to user.

        Args:
            user_id (str): Specify the user ID.

            comment (str): Specify the comment.

        Endpoint:
            :code:`users/report-abuse`

        Returns:
            bool: Returns :code:`True` if the report is sent.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/report-abuse', **params)

    def users_clips(
        self,
        user_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of clips created by the specified user.

        Args:
            user_id (str): Specifies the user ID.

            limit (int, default: :code:`10`): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`users/clips`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of clips.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/clips', **params)

    def users(
        self,
        limit: int = 10,
        offset: int = 0,
        alive_only: bool = False,
        origin: Union[UserOrigin, str] = UserOrigin.LOCAL,
        sort_key: Union[
            UserSortKey,
            str,
        ] = UserSortKey.FOLLOWER,
        sort_asc: bool = False,
        hostname: Optional[str] = None,
    ) -> List[dict]:
        """Get a list of users.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            offset (int, default: 0): Specifies the offset to get.

            alive_only (bool, default: :code:`False`): Specifies whether to
            only get users active in 5 days.

            origin (str, default: :code:`local`): Specifies the origin type of
            users to get. Available values are enumerated in
            :class:`enum.UserOrigin`. If :code:`combined`, both :code:`local`
            and :code:`remote` users are included in the result.

            sort_key (str, default: :code:`follower`):
            Specifies sort key. Available values are enumerated in
            :class:`enum.UserSortKey`.

            sort_asc (bool, default: :code:`False`): Specifies the sort order.
            Hashtags sort in ascending order according to the key specified
            with :obj:`sort_key` if :code:`True`, descending order if
            :code:`False`.

            hostname (str, optional): Specifies the host to search. The local
            host is represented with :code:`None`.

        Endpoint:
            :code:`users`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`origin` or :code:`sort_key` is invalid.
        """
        state = 'alive' if alive_only else 'all'
        if type(origin) is str:
            origin = UserOrigin(origin)
        if type(sort_key) is str:
            sort_key = UserSortKey(sort_key)
        sort = '-' if sort_asc else '+'
        sort += sort_key.value
        del alive_only, sort_key, sort_asc
        params = self.__params(locals())
        return self.__request_api('users', **params)

    def users_gallery_posts(
        self,
        user_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Show all gallery posts created by the specified user.

        Args:
            user_id (str): Specifies the user ID.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`users/gallery/posts`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of gallery posts.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/gallery/posts', **params)

    def users_get_frequently_replied_users(
        self,
        user_id: str,
        limit: int = 10,
    ) -> List[dict]:
        """Get list of users sorted by the number of replies sent by the
        specified user.

        Args:
            user_id (str): Specifies the user ID.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

        Endpoint:
            :code:`users/get-frequently-replied-users`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes and weights.
            Weight is defined as number of replies the user accepted divided by
            the maximum number of replies the sender sent to a user.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'users/get-frequently-replied-users',
            userId=user_id,
        )

    def users_pages(
        self,
        user_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Show all pages created by the specified user.

        Args:
            user_id (str): Specifies the user ID.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`users/pages`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of pages.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/pages', **params)

    def users_reactions(
        self,
        user_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Optional[Union[int, datetime.datetime]] = None,
        until_date: Optional[Union[int, datetime.datetime]] = None,
    ) -> List[dict]:
        """Get reactions created by the specified user.

        Args:
            user_id (str): Specifies the user ID.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            since_date (:obj:`datetime.datetime`, optional): Specifies
            the first date to get.

            since_date (:obj:`datetime.datetime`, optional): Specifies
            the last date to get.

        Endpoint:
            :code:`users/reactions`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of reactions.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('users/reactions', **params)

    def users_search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        origin: Union[UserOrigin, str] = UserOrigin.LOCAL,
        detail: bool = True,
    ) -> List[dict]:
        """Search for users.

        Args:
            query(str): Specifies the search query. If starts with :code:`@`,
            search for users whose username starts with the query. Otherwise,
            search for users that contain query in their display name,
            username or profiles.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            offset (int, default: 0): Specifies the offset to get.

            origin (str, default: :code:`local`): Specifies the origin type of
            users to get. Available values are enumerated in
            :class:`enum.UserOrigin`. If :code:`combined`, both :code:`local`
            and :code:`remote` users are included in the result.

            detail (bool, default: :code:`True`): Specifies whether to get
            detailed profiles.

        Endpoint:
            :code:`users/search`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of users. Those
            inactive for more than 30 days or suspended users are excluded from
            the result. Sorted by the last note created by the user, in reverse
            chronological order.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`origin` is invalid.
        """
        if type(origin) is str:
            origin = UserOrigin(origin)
        params = self.__params(locals())
        return self.__request_api('users/search', **params)

    def users_search_by_username_and_host(
        self,
        username: Optional[str] = None,
        host: Optional[str] = None,
        limit: int = 10,
        detail: bool = True,
    ) -> List[dict]:
        """Search for users by username and host.

        Args:
            username (str, optional): Specifies the username to search.

            host (str, optional): Specifies the host to search.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            detail (bool, default: :code:`True`): Specifies whether to get
            detailed profiles.

        Endpoint:
            :code:`users/search-by-username-and-host`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of users. Those
            inactive for more than 30 days or suspended users are excluded from
            the result. Sorted by the last note created by the user, in reverse
            chronological order.

        Note:
            You must specify at least any of :code:`username` or :code:`host`.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api(
            'users/search-by-username-and-host',
            **params
        )

    def email_address_available(
        self,
        email_address: str,
    ) -> dict:
        """Check if the email address is available for the instance.

        Args:
            email_address (str): Specifies the email address.

        Endpoint:
            :code:`email-address/available`

        Returns:
            dict: Returns whether the address is available and the reason if
            unavailable.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'email-address/available',
            emailAddress=email_address
        )

    def pinned_users(self) -> List[dict]:
        """Get a list of users pinned by the administrator of the instance.

        Endpoint:
            :code:`pinned-users`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('pinned-users')

    def username_available(
        self,
        username: str,
    ) -> dict:
        """Check if the username is available for the instance.

        Args:
            username (str): Specifies the username.

        Endpoint:
            :code:`username/available`

        Returns:
            dict: Returns whether the username is available.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('username/available', **params)

    def following_create(
        self,
        user_id: str,
    ) -> dict:
        """Follow the specified user.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`following/create`

        Returns:
            dict: Returns the following information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('following/create', userId=user_id)

    def following_delete(
        self,
        user_id: str,
    ) -> dict:
        """Unfollow the specified user.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`following/delete`

        Returns:
            dict: Returns the following information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('following/delete', userId=user_id)

    def following_invalidate(
        self,
        user_id: str,
    ) -> dict:
        """Invalidate follow from the specified user.

        Args:
            user_id (str): Specifies the user ID.

        Endpoint:
            :code:`following/invalidate`

        Returns:
            dict: Returns the following information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('following/invalidate', userId=user_id)

    def mute_create(
        self,
        user_id: str,
        expires_at: Optional[Union[int, datetime.datetime]] = None,
    ) -> bool:
        """Mute the specified user.

        Args:
            user_id (str): Specify the user ID.

            expires_at (:obj:`datetime.datetime`, optional): Specifies the date
            the mute expires at. If :code:`None`, mute indefinitely.

        Endpoint:
            :code:`mute/create`

        Returns:
            bool: Returns :code:`True` if the user is muted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(expires_at, datetime.datetime):
            expires_at = math.floor(expires_at.timestamp() * 1000)
        return self.__request_api('mute/create', userId=user_id)

    def mute_list(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of muted users.

        Args:
            limit (int): Specify the number of users to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

        Endpoint:
            :code:`mute/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of muted users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('mute/list', **params)

    def mute_delete(
        self,
        user_id: str,
    ) -> bool:
        """Unmute the specified user.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`mute/delete`

        Returns:
            bool: Returns :code:`True` if the user is unmuted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('mute/delete', userId=user_id)

    def blocking_create(
        self,
        user_id: str,
    ) -> dict:
        """Block the specified user.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`blocking/create`

        Returns:
            dict: Returns the blocking information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('blocking/create', userId=user_id)

    def blocking_list(
        self,
        limit: int = 30,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of blocked users.

        Args:
            limit (int): Specify the number of users to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

        Endpoint:
            :code:`blocking/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of blocked users.
        """
        params = self.__params(locals())
        return self.__request_api('blocking/list', **params)

    def blocking_delete(
        self,
        user_id: str,
    ) -> dict:
        """Unblock the specified user.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`blocking/delete`

        Returns:
            dict: Returns the blocking information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('blocking/delete', userId=user_id)

    def following_requests_accept(
        self,
        user_id: str,
    ) -> bool:
        """Accept the following request.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`following/requests/accept`

        Returns:
            bool: Returns :code:`True` if the request is successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'following/requests/accept',
            userId=user_id
        )

    def following_requests_reject(
        self,
        user_id: str,
    ) -> bool:
        """Reject the following request.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`following/requests/reject`

        Returns:
            bool: Returns :code:`True` if the request is successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'following/requests/reject',
            userId=user_id,
        )

    def following_requests_cancel(
        self,
        user_id: str,
    ) -> dict:
        """Cancel the following request.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`following/requests/cancel`

        Returns:
            dict: Returns the following information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'following/requests/cancel',
            userId=user_id,
        )

    def following_requests_list(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of following requests.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.


        Endpoint:
            :code:`following/requests/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of following requests.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('following/requests/list', **params)

    def drive(self) -> dict:
        """Get drive usage information.

        Endpoint:
            :code:`drive`

        Returns:
            dict: Returns the drive usage information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('drive')

    def drive_stream(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> List[dict]:
        """Get drive files.

        Args:
            limit (int): Specify the number of files to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            file_type (str, optional): Specify the file type.

        Endpoint:
            :code:`drive/stream`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of files.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(
            locals(),
            custom_rename={
                'file_type': 'type',
            },
        )
        return self.__request_api('drive/stream', **params)

    def drive_files(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> List[dict]:
        """Get drive files in specified folder(optional).

        Args:
            limit (int): Specify the number of files to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            folder_id (str, optional): Specify the folder ID.

            file_type (str, optional): Specify the file type.

        Endpoint:
            :code:`drive/files`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of files.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(
            locals(),
            custom_rename={
                'file_type': 'type',
            },
        )
        return self.__request_api('drive/files', **params)

    def drive_files_create(
        self,
        file: IOTypes,
        folder_id: Optional[str] = None,
        name: Optional[str] = None,
        is_sensitive: bool = False,
        force: bool = False,
    ) -> dict:
        """Upload a file to the drive.

        Args:
            file (:obj:`IO`): Assign a file stream. As an example,
            the one opened by the :obj:`open` function is included.

            folder_id (str, optional): Specify the folder ID.

            name (str, optional): Specify the file name.

            is_sensitive (bool, optional): Specify whether the file is
            sensitive.

            force (bool, optional): Specify whether to overwrite the file
            if it already exists.

        Endpoint:
            :code:`drive/files/create`

        Returns:
            dict: Returns the file information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals(), {'file', 'is_sensitive', 'force'})
        params.update(
            i=self.__token,
            isSensitive=str(is_sensitive).lower(),
            force=str(force).lower()
        )
        response = self.__session.post(
            f'{self.__api_url}/drive/files/create',
            data=params,
            files={
                'file': file,
            },
            allow_redirects=False,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise MisskeyAPIException(response.json())

        return response.json()

    def drive_files_check_existence(
        self,
        md5: str,
    ) -> bool:
        """Validate if the specified md5 hash exists in the drive.

        Args:
            md5 (str): Specify the md5 hash.

        Endpoint:
            :code:`drive/files/check-existence`

        Returns:
            bool: Returns :code:`True` if the file exists.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('drive/files/check-existence', md5=md5)

    def drive_files_attached_notes(
        self,
        file_id: str,
    ) -> List[dict]:
        """Get notes that have the specified file.

        Args:
            file_id (str): Specify the file ID.

        Endpoint:
            :code:`drive/files/attached-notes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'drive/files/attached-notes',
            fileId=file_id
        )

    def drive_files_find_by_hash(
        self,
        md5: str,
    ) -> List[dict]:
        """Get files that have the specified md5 hash.

        Args:
            md5 (str): Specify the md5 hash.

        Endpoint:
            :code:`drive/files/find-by-hash`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of files.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'drive/files/find-by-hash',
            md5=md5,
        )

    def drive_files_show(
        self,
        file_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> dict:
        """Get file information.

        Args:
            file_id (str, optional): Specify the file ID.

            url (str, optional): Specify the file URL.

        Endpoint:
            :code:`drive/files/show`

        Note:
            You need to specify either :obj:`file_id` or :obj:`url`.

        Returns:
            dict: Returns the file information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api(
            'drive/files/show',
            **params
        )

    def drive_files_update(
        self,
        file_id: str,
        folder_id: Union[str, None] = '',
        name: Optional[str] = None,
        is_sensitive: Optional[bool] = None,
        comment: Union[str, None] = '',
    ) -> dict:
        """Update file information.

        Args:
            file_id (str): Specify the file ID.

            folder_id (str, optional): Specify the folder ID.

            name (str, optional): Specify the file name.

            is_sensitive (bool, optional): Specify whether the file is
            sensitive.

            comment (str, optional): Specify a comment.

        Endpoint:
            :code:`drive/files/update`

        Returns:
            dict: Returns the file information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals(), {'folder_id', 'comment'})
        if folder_id != '':
            params['folderId'] = folder_id
        if comment != '':
            params['comment'] = comment

        return self.__request_api('drive/files/update', **params)

    def drive_files_delete(
        self,
        file_id: str,
    ) -> bool:
        """Delete a file.

        Args:
            file_id (str): Specify the file ID.

        Endpoint:
            :code:`drive/files/delete`

        Returns:
            bool: Returns :code:`True` if the file is deleted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('drive/files/delete', fileId=file_id)

    def drive_files_find(
        self,
        name: str,
        folder_id: Optional[str] = None,
    ) -> List[dict]:
        """Get files with the specified name.

        Args:
            name (str): Specifies the file name.

            folder_id (Optional[str]): Specifies the folder ID of the parent
            folder. If :code:`None`, search files in root folder.

        Endpoint:
            :code:`drive/files/find`

        Returns:
            List[dict]: Returns the list of files.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('drive/files/find', **params)

    def drive_files_upload_from_url(
        self,
        url: str,
        folder_id: Optional[str] = None,
        is_sensitive: bool = False,
        comment: Optional[str] = None,
        marker: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Upload a file specified with the source URL to the drive.

        Args:
            url (str): Specifies the URL where the file content locates.

            folder_id (str, optional): Specifies the folder ID.

            is_sensitive (bool, default: :code:`False`): Specifies whether the
            file is sensitive.

            comment (str, optional): Specifies the caption of the file.

            marker (str, optional): Specifies the marker to track the upload.

            force (bool, optional): Specifies whether to overwrite the file
            if it already exists.

        Endpoint:
            :code:`drive/files/upload-from-url`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('drive/files/upload-from-url', **params)

    def drive_folders(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> List[dict]:
        """Get the folder list.

        Args:
            limit (int, optional): Specify the number of folders to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specify the first ID to get.

            until_id (str, optional): Specify the last ID to get.

            folder_id (str, optional): Specify the folder ID.

        Endpoint:
            :code:`drive/folders`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of folders.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('drive/folders', **params)

    def drive_folders_create(
        self,
        name: str = 'Untitled',
        parent_id: Optional[str] = None,
    ) -> dict:
        """Create a folder.

        Args:
            name (str, optional): Specify the folder name.

            parent_id (str, optional): Specify the parent folder ID.

        Endpoint:
            :code:`drive/folders/create`

        Returns:
            dict: Returns the folder information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('drive/folders/create', **params)

    def drive_folders_show(
        self,
        folder_id: str,
    ) -> dict:
        """Get folder information.

        Args:
            folder_id (str): Specify the folder ID.

        Endpoint:
            :code:`drive/folders/show`

        Returns:
            dict: Returns the folder information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'drive/folders/show',
            folderId=folder_id
        )

    def drive_folders_update(
        self,
        folder_id: str,
        name: Optional[str] = None,
        parent_id: Union[str, None] = '',
    ) -> dict:
        """Update folder information.

        Args:
            folder_id (str): Specify the folder ID.

            name (str, optional): Specify the folder name.

            parent_id (str, optional): Specify the parent folder ID.

        Endpoint:
            :code:`drive/folders/update`

        Returns:
            dict: Returns the folder information.
        """
        params = self.__params(locals(), {'parent_id'})
        if parent_id != '':
            params['parentId'] = parent_id
        return self.__request_api('drive/folders/update', **params)

    def drive_folders_delete(
        self,
        folder_id: str,
    ) -> bool:
        """Delete a folder.

        Args:
            folder_id (str): Specify the folder ID.

        Endpoint:
            :code:`drive/folders/delete`

        Returns:
            bool: Returns :code:`True` if the folder is deleted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'drive/folders/delete',
            folderId=folder_id
        )

    def drive_folders_find(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> List[dict]:
        """Get folders with the specified name.

        Args:
            name (str): Specifies the folder name.

            folder_id (Optional[str]): Specifies the folder ID of the parent
            folder. If :code:`None`, search folders in root folder.

        Endpoint:
            :code:`drive/folders/find`

        Returns:
            List[dict]: Returns the list of folders.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('drive/folders/find', **params)

    def antennas_create(
        self,
        name: str,
        src: Union[AntennaSource, str] = AntennaSource.ALL,
        user_list_id: Optional[str] = None,
        keywords: List[List[str]] = [[]],
        exclude_keywords: List[List[str]] = [[]],
        users: List[str] = [],
        case_sensitive: bool = False,
        with_replies: bool = False,
        with_file: bool = False,
        notify: bool = False,
    ) -> dict:
        """Create an antenna.

        Args:
            name (str): Specifies the name of the antenna.

            src (str, default: :code:`all`): Specifies antenna source.
            Available values are enumerated in :class:`enum.AntennaSource`.

            user_list_id (str, optional):
            If :code:`src` is :code:`list`, specifies the list ID.

            keywords
            (:obj:`list` of :obj:`list` of :obj:`str`, default: :code:`[[]]`):
            Specifies keywords to listen to. Keywords in the inner list join
            with AND conditions and the outer list with OR conditions.

            exclude_keywords
            (:obj:`list` of :obj:`list` of :obj:`str`, default: :code:`[[]]`):
            Specifies keywords to exclude. Keywords in the inner list join with
            AND conditions and the outer list with OR conditions.

            users (:obj:`list` of :obj:`str`, default: :code:`[]`):
            Specifies usernames of users to listen to.

            case_sensitive (bool, default: :code:`False`):
            Specifies whether keywords are case sensitive.

            with_replies (bool, default: :code:`False`):
            Specifies whether to include replies.

            with_file (bool, default: :code:`False`):
            Specifies whether to listen only to notes with files.

            notify (bool, default: :code:`False`):
            Specifies whether to notify about new notes.

        Endpoint:
            :code:`antennas/create`

        Note:
            If :code:`src` is :code:`list`,
            :code:`user_list_id` must be specified.

        Returns:
            dict: Returns the created antenna information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`src` is invalid.
        """
        if type(src) is str:
            src = AntennaSource(src)

        params = self.__params(locals())
        return self.__request_api('antennas/create', **params)

    def antennas_delete(
        self,
        antenna_id: str,
    ) -> bool:
        """Delete an antenna.

        Args:
            antenna_id (str): Specifies the antenna ID.

        Endpoint:
            :code:`antennas/delete`

        Returns:
            bool: Returns :code:`True` if the antenna is deleted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('antennas/delete', antennaId=antenna_id)

    def antennas_list(self) -> List[dict]:
        """Get list of antennas.

        Endpoint:
            :code:`antennas/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of antennas.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('antennas/list')

    def antennas_notes(
        self,
        antenna_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
    ) -> List[dict]:
        """Get notes from the specified antenna.

        Args:
            antenna_id (str): Specifies the antenna ID.

            limit (int, default: :code:`10`): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            since_date (int, datetime.datetime, optional): Specifies
            the first date to get.

            until_date (int, datetime.datetime, optional): Specifies
            the last date to get.


        Endpoint:
            :code:`antennas/notes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(until_date.timestamp() * 1000)

        params = self.__params(locals())
        return self.__request_api('antennas/notes', **params)

    def antennas_show(
        self,
        antenna_id: str
    ) -> dict:
        """Get user antenna detail.

        Args:
            antenna_id (str): Specifies the antenna ID.

        Endpoint:
            :code:`antennas/show`

        Returns:
            dict: Returns the antenna information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('antennas/show', antennaId=antenna_id)

    def antennas_update(
        self,
        antenna_id: str,
        name: str,
        src: Union[AntennaSource, str] = AntennaSource.ALL,
        user_list_id: Optional[str] = None,
        keywords: List[List[str]] = [[]],
        exclude_keywords: List[List[str]] = [[]],
        users: List[str] = [],
        case_sensitive: bool = False,
        with_replies: bool = False,
        with_file: bool = False,
        notify: bool = False,
    ) -> dict:
        """Update an antenna.

        Args:
            antenna_id (str): Specifies the antenna ID to update.

            name (str): Specifies the name of the antenna.

            src (str, default: :code:`all`): Specifies antenna source.
            Available values are enumerated in :class:`enum.AntennaSource`.

            user_list_id (str, optional):
            If :code:`src` is :code:`list`, specifies the list ID.

            keywords
            (:obj:`list` of :obj:`list` of :obj:`str`, default: :code:`[[]]`):
            Specifies keywords to listen to. Keywords in the inner list join
            with AND conditions and the outer list with OR conditions.

            exclude_keywords
            (:obj:`list` of :obj:`list` of :obj:`str`, default: :code:`[[]]`):
            Specifies keywords to exclude. Keywords in the inner list join with
            AND conditions and the outer list with OR conditions.

            users (:obj:`list` of :obj:`str`, default: :code:`[]`):
            Specifies usernames of users to listen to.

            case_sensitive (bool, default: :code:`False`):
            Specifies whether keywords are case sensitive.

            with_replies (bool, default: :code:`False`):
            Specifies whether to include replies.

            with_file (bool, default: :code:`False`):
            Specifies whether to listen only to notes with files.

            notify (bool, default: :code:`False`):
            Specifies whether to notify about new notes.

        Endpoint:
            :code:`antennas/update`

        Note:
            If :code:`src` is :code:`list`, :code:`user_list_id` must be
            specified.

            If you do not specify any of arguments, the corresponding parts of
            your antenna settings will be updated with the default values.

        Returns:
            dict: Returns the updated antenna information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`src` is invalid.
        """
        if type(src) is str:
            src = AntennaSource(src)

        params = self.__params(locals())
        return self.__request_api('antennas/update', **params)

    def channels_create(
        self,
        name: str,
        description: Optional[str] = None,
        banner_id: Optional[str] = None,
    ) -> dict:
        """Create a channel.

        Args:
            name (str): Specifies the name of the channel.

            description (str, optional):
            Specifies the description of the channel.

            banner_id (str, optional):
            Specifies the file ID of the banner image for the channel.

        Endpoint:
            :code:`channels/create`

        Returns:
            dict: Returns the created channel information.

        Note:
            Once you have created a channel, it cannot be deleted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('channels/create', **params)

    def channels_featured(self) -> List[dict]:
        """Get list of featured channels.

        Endpoint:
            :code:`channels/featured`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of featured channels.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('channels/featured')

    def channels_follow(
        self,
        channel_id: str,
    ) -> bool:
        """Follow the specified channel.

        Args:
            channel_id (str): Specifies the channel ID to follow.

        Endpoint:
            :code:`channels/follow`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('channels/follow', channelId=channel_id)

    def channels_followed(
        self,
        limit: int = 5,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of channels you are following.

        Args:
            limit (int, default: 5): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`channels/followed`

        Returns:
            :obj:`list` of :obj:`dict`:
            Returns the list of channels you are following.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('channels/followed', **params)

    def channels_owned(
        self,
        limit: int = 5,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of channels you have created.

        Args:
            limit (int, default: 5): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`channels/owned`

        Returns:
            :obj:`list` of :obj:`dict`:
            Returns the list of channels you have created.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('channels/owned', **params)

    def channels_show(
        self,
        channel_id: str,
    ) -> dict:
        """Get channel details.

        Args:
            channel_id (str): Specifies the channel ID to get.

        Endpoint:
            :code:`channels/show`

        Returns:
            dict: Returns the channel information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('channels/show', channelId=channel_id)

    def channels_timeline(
        self,
        channel_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        since_date: Union[int, datetime.datetime, None] = None,
        until_date: Union[int, datetime.datetime, None] = None,
    ) -> List[dict]:
        """Get notes from the specified channel.

        Args:
            channel_id (str): Specifies the channel ID to get.

            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

            since_date (int, datetime.datetime, optional): Specifies
            the first date to get.

            until_date (int, datetime.datetime, optional): Specifies
            the last date to get.

        Endpoint:
            :code:`channels/timeline`

        Returns:
            :obj:`list` of :obj:`dict`:
            Returns the list of notes from the channel.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        if isinstance(since_date, datetime.datetime):
            since_date = math.floor(since_date.timestamp() * 1000)
        if isinstance(until_date, datetime.datetime):
            until_date = math.floor(until_date.timestamp() * 1000)
        params = self.__params(locals())
        return self.__request_api('channels/timeline', **params)

    def channels_unfollow(
        self,
        channel_id: str,
    ) -> bool:
        """Unfollow the specified channel.

        Args:
            channel_id (str): Specifies the channel ID to unfollow.

        Endpoint:
            :code:`channels/unfollow`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('channels/unfollow', channelId=channel_id)

    def channels_update(
        self,
        channel_id: str,
        name: str,
        description: Optional[str] = None,
        banner_id: Optional[str] = None,
    ) -> dict:
        """Update a channel.

        Args:
            channel_id (str): Specifies the channel ID to update.

            name (str): Specifies the name of the channel.

            description (str, optional):
            Specifies the description of the channel.

            banner_id (str, optional):
            Specifies the file ID of the banner image for the channel.

        Note:
            If you do not specify any of arguments, the corresponding parts of
            your channel settings will be updated with the default values.

        Endpoint:
            :code:`channels/update`

        Returns:
            dict: Returns the updated channel information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('channels/update', **params)

    def charts_active_users(
        self,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of active users.

        Args:
            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/active-users`

        Returns:
            dict: Returns the active users chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/active-users', **params)

    def charts_ap_request(
        self,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of ActivityPub requests amount.

        Args:
            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/ap-request`

        Returns:
            dict: Returns the ActivityPub request chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/ap-request', **params)

    def charts_drive(
        self,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of drive file difference.

        Args:
            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/drive`

        Returns:
            dict: Returns the drive chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/drive', **params)

    def charts_federation(
        self,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of federation.

        Args:
            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/federation`

        Returns:
            dict: Returns the federation chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/federation', **params)

    def charts_instance(
        self,
        host: str,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of the specified instance.

        Args:
            host (str): Specifies the host of the instance.

            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/instance`

        Returns:
            dict: Returns the instance chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/instance', **params)

    def charts_notes(
        self,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of notes.

        Args:
            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/notes`

        Returns:
            dict: Returns the notes chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/notes', **params)

    def charts_user_drive(
        self,
        user_id: str,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of drive usage of the specified user.

        Args:
            user_id (str): Specifies the user ID.

            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/user/drive`

        Returns:
            dict: Returns the user drive chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/user/drive', **params)

    def charts_user_following(
        self,
        user_id: str,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of following and followers number of the specified user.

        Args:
            user_id (str): Specifies the user ID.

            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/user/following`

        Returns:
            dict: Returns the user following chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/user/following', **params)

    def charts_user_notes(
        self,
        user_id: str,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of notes of the specified user.

        Args:
            user_id (str): Specifies the user ID.

            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/user/notes`

        Returns:
            dict: Returns the user notes chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/user/notes', **params)

    def charts_user_pv(
        self,
        user_id: str,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of profile view count of the specified user.

        Args:
            user_id (str): Specifies the user ID.

            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/user/pv`

        Returns:
            dict: Returns the user pv chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/user/pv', **params)

    def charts_user_reactions(
        self,
        user_id: str,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of received reactions of the specified user.

        Args:
            user_id (str): Specifies the user ID.

            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/user/reactions`

        Returns:
            dict: Returns the user reactions chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/user/reactions', **params)

    def charts_users(
        self,
        span: Union[ChartSpan, str] = ChartSpan.DAY,
        limit: int = 30,
        offset: Optional[int] = None,
    ) -> dict:
        """Get chart of users.

        Args:
            span (str, default: :code:`day`):
            Specifies spans of single items in the chart.

            limit (int, default: :code:`30`): Specifies the amount to get.
            You can specify from 1 to 500.

            offset (int, optional): Specifies the offset to get.

        Endpoint:
            :code:`charts/users`

        Returns:
            dict: Returns the users chart.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`span` is invalid.
        """
        if type(span) is str:
            span = ChartSpan(span)
        params = self.__params(locals())
        return self.__request_api('charts/users', **params)

    def clips_add_note(
        self,
        clip_id: str,
        note_id: str,
    ) -> bool:
        """Add a note to the specified clip.

        Args:
            clip_id (str): Specifies the clip ID to add the note.

            note_id (str): Specifies the note ID to add.

        Endpoint:
            :code:`clips/add-note`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('clips/add-note', **params)

    def clips_create(
        self,
        name: str,
        is_public: bool = False,
        description: Optional[str] = None,
    ) -> dict:
        """Create a clip.

        Args:
            name (str): Specifies the clip name.

            is_public (bool, default: :code:`False`):
            Whether to reveal the clip to other users.

            description (str, optional): Specifies the description of the clip.

        Endpoint:
            :code:`clips/create`

        Returns:
            dict: Returns the created clip.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('clips/create', **params)

    def clips_delete(
        self,
        clip_id: str
    ) -> bool:
        """Delete a clip.

        Args:
            clip_id (str): Specifies the clip ID to delete.

        Endpoint:
            :code:`clips/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('clips/delete', clipId=clip_id)

    def clips_list(self) -> List[dict]:
        """Get list of clips you have created.

        Endpoint:
            :code:`clips/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of clips.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('clips/list')

    def clips_notes(
        self,
        clip_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get notes in the specified clip.

        Args:
            clip_id (str): Specifies the clip ID.

            limit (int, default: :code:`10`): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`clips/notes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of notes.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('clips/notes', **params)

    def clips_remove_note(
        self,
        clip_id: str,
        note_id: str,
    ) -> bool:
        """Remove a note from the specified clip.

        Args:
            clip_id (str): Specifies the clip ID to remove the note.

            note_id (str): Specifies the note ID to remove.

        Endpoint:
            :code:`clips/remove-note`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('clips/remove-note', **params)

    def clips_show(
        self,
        clip_id: str,
    ) -> dict:
        """Get clip information.

        Args:
            clip_id (str): Specifies the clip ID.

        Endpoint:
            :code:`clips/show`

        Returns:
            dict: Returns the clip information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('clips/show', clipId=clip_id)

    def clips_update(
        self,
        clip_id: str,
        name: str,
        is_public: bool = False,
        description: Optional[str] = None,
    ) -> dict:
        """Update the clip information.

        Args:
            clip_id (str): Specifies the clip ID to update.

            name (str): Specifies the clip name.

            is_public (bool, default: :code:`False`):
            Whether to reveal the clip to other users.

            description (str, optional): Specifies the description of the clip.

        Endpoint:
            :code:`clips/update`

        Returns:
            dict: Returns the updated clip.

        Note:
            If you do not specify any of arguments, the corresponding parts of
            your clip settings will be updated with the default values.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('clips/update', **params)

    def flash_create(
        self,
        title: str,
        summary: str,
        script: str,
        permissions: List[str] = [],
    ) -> dict:
        """Create a Play.

        Args:
            title (str): Specifies the title of the Play.

            summary (str): Specifies the description of the Play.

            script (str): Specifies the script of the Play.

            permissions (:obj:`list` of :obj:`str`, default: :code:`[]`):
            Specifies permissions.

        Endpoint:
            :code:`flash/create`

        Returns:
            dict: Returns the created Play information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('flash/create', **params)

    def flash_delete(
        self,
        flash_id: str,
    ) -> List[dict]:
        """Delete a Play.

        Args:
            flash_id (str): Specifies the Play ID.

        Endpoint:
            :code:`flash/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('flash/delete', flashId=flash_id)

    def flash_featured(self) -> List[dict]:
        """Get list of featured Plays.

        Endpoint:
            :code:`flash/featured`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of featured Plays.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('flash/featured', **params)

    def flash_like(
        self,
        flash_id: str,
    ) -> bool:
        """Like the specified Play.

        Args:
            flash_id (str): Specifies the Play ID.

        Endpoint:
            :code:`flash/like`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('flash/like', flashId=flash_id)

    def flash_my(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of Plays you have created.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`flash/my`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of Plays.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('flash/my', **params)

    def flash_my_likes(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of Plays you have liked.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`flash/my-likes`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of Plays.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('flash/my-likes', **params)

    def flash_show(
        self,
        flash_id: str,
    ) -> dict:
        """Get Play details.

        Args:
            flash_id (str): Specifies the Play ID to get.

        Endpoint:
            :code:`flash/show`

        Returns:
            dict: Returns the Play information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('flash/show', flashId=flash_id)

    def flash_unlike(
        self,
        flash_id: str,
    ) -> bool:
        """Unlike the specified Play.

        Args:
            flash_id (str): Specifies the Play ID.

        Endpoint:
            :code:`flash/unlike`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('flash/unlike', flashId=flash_id)

    def flash_update(
        self,
        flash_id: str,
        title: str,
        summary: str,
        script: str,
        permissions: List[str] = [],
    ) -> bool:
        """Update the Play information.

        Args:
            flash_id (str): Specifies the Play ID.

            title (str): Specifies the title of the Play.

            summary (str): Specifies the description of the Play.

            script (str): Specifies the script of the Play.

            permissions (:obj:`list` of :obj:`str`, default: :code:`[]`):
            Specifies permissions.

        Endpoint:
            :code:`flash/update`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('flash/update', **params)

    def gallery_featured(self) -> List[dict]:
        """Get list of featured gallery posts.

        Endpoint:
            :code:`gallery/featured`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of featured gallery
            posts.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('gallery/featured')

    def gallery_popular(self) -> List[dict]:
        """Get list of popular gallery posts.

        Endpoint:
            :code:`gallery/popular`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of popular gallery
            posts.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('gallery/popular')

    def gallery_posts(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        """Get list of gallery posts.

        Args:
            limit (int, default: 10): Specifies the amount to get.
            You can specify from 1 to 100.

            since_id (str, optional): Specifies the first ID to get.

            until_id (str, optional): Specifies the last ID to get.

        Endpoint:
            :code:`gallery/posts`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of gallery posts.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('gallery/posts', **params)

    def gallery_posts_create(
        self,
        title: str,
        file_ids: List[str],
        description: Optional[str] = None,
        is_sensitive: bool = False,
    ) -> dict:
        """Create a gallery post.

        Args:
            title (str): Specifies the title of the post.

            file_ids (:obj:`list` of :obj:`str`): Specifies the file ID to
            attach to the post.

            description (str, optional): Specifies the description of the post.

            is_sensitive (bool, default: :code:`False`): Specifies whether the
            files are sensitive.

        Endpoint:
            :code:`gallery/posts/create`

        Returns:
            dict: Returns the created gallery post information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('gallery/posts/create', **params)

    def gallery_posts_delete(
        self,
        post_id: str,
    ) -> bool:
        """Delete a gallery post.

        Args:
            post_id (str): Specifies the gallery post ID.

        Endpoint:
            :code:`gallery/posts/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('gallery/posts/delete', postId=post_id)

    def gallery_posts_like(
        self,
        post_id: str,
    ) -> bool:
        """Like the specified gallery post.

        Args:
            post_id (str): Specifies the gallery post ID.

        Endpoint:
            :code:`gallery/posts/like`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('gallery/posts/like', postId=post_id)

    def gallery_posts_show(
        self,
        post_id: str,
    ) -> dict:
        """Get the gallery post information.

        Args:
            post_id (str): Specifies the gallery post ID.

        Endpoint:
            :code:`gallery/posts/show`

        Returns:
            dict: Returns the gallery post information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('gallery/posts/show', postId=post_id)

    def gallery_posts_unlike(
        self,
        post_id: str,
    ) -> bool:
        """Unlike the specified gallery post.

        Args:
            post_id (str): Specifies the gallery post ID.

        Endpoint:
            :code:`gallery/posts/unlike`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('gallery/posts/unlike', postId=post_id)

    def gallery_posts_update(
        self,
        post_id: str,
        title: str,
        file_ids: List[str],
        description: Optional[str] = None,
        is_sensitive: bool = False,
    ) -> dict:
        """Update a gallery post.

        Args:
            post_id (str): Specifies the gallery post ID.

            title (str): Specifies the title of the post.

            file_ids (:obj:`list` of :obj:`str`): Specifies the file ID to
            attach to the post.

            description (str, optional): Specifies the description of the post.

            is_sensitive (bool, default: :code:`False`): Specifies whether the
            files are sensitive.

        Endpoint:
            :code:`gallery/posts/update`

        Returns:
            dict: Returns the updated gallery post information.

        Note:
            If you do not specify any of arguments, the corresponding parts of
            your gallery settings will be updated with the default values.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('gallery/posts/update', **params)

    def hashtags_list(
        self,
        limit: int = 10,
        attached_to_user_only: bool = False,
        attached_to_local_user_only: bool = False,
        attached_to_remote_user_only: bool = False,
        sort_key: Union[
            HashtagsListSortKey,
            str,
        ] = HashtagsListSortKey.MENTIONED_USERS,
        sort_asc: bool = False,
    ) -> List[dict]:
        """Get list of hashtags.

        Args:
            limit (int, default: :code:`10`): Specifies the amount to get.
            You can specify from 1 to 100.

            attached_to_user_only (bool, default: :code:`False`): Specifies
            whether to exclude hashtags that are not attached to user profiles.

            attached_to_local_user_only (bool, default: :code:`False`):
            Specifies whether to exclude hashtags that are not attached to
            local user profiles.

            attached_to_remote_user_only (bool, default: :code:`False`):
            Specifies whether to exclude hashtags that are not attached to
            remote user profiles.

            sort_key (str, default: :code:`mentionedUsers`):
            Specifies sort key. Available values are enumerated in
            :class:`enum.HashtagsListSortKey`.

            sort_asc (bool, default: :code:`False`): Specifies the sort order.
            Hashtags sort in ascending order according to the key specified
            with :obj:`sort_key` if :code:`True`, descending order if
            :code:`False`.

        Endpoint:
            :code:`hashtags/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of hashtags.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`origin` or :code:`sort_key` is invalid.
        """
        if type(sort_key) is str:
            sort_key = HashtagsListSortKey(sort_key)
        sort = '-' if sort_asc else '+'
        sort += sort_key.value
        del sort_key, sort_asc
        params = self.__params(locals())
        return self.__request_api('hashtags/list', **params)

    def hashtags_search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> List[dict]:
        """Search hashtags that start with the specified query.

        Args:
            query (str): Specify search query.

            limit (int, default: :code:`10`): Specifies the amount to get.
            You can specify from 1 to 100.

            offset (int, default: :code:`0`): Specifies the offset to get.

        Endpoint:
            :code:`hashtags/search`

        Returns:
            :obj:`list` of :obj:`dict`: Returns a list of hashtags sorted in
            descending order of use count.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('hashtags/search', **params)

    def hashtags_show(
        self,
        tag: str,
    ) -> dict:
        """Get information of the specified hashtag.

        Args:
            tag (str): Specifies the hashtag to search.

        Endpoint:
            :code:`hashtags/show`

        Returns:
            dict: Returns the hashtag information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('hashtags/show', tag=tag)

    def hashtags_trend(self) -> List[dict]:
        """Get hashtags on trend.

        Endpoint:
            :code:`hashtags/trend`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of hashtag charts.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('hashtags/trend')

    def hashtags_users(
        self,
        tag: str,
        limit: int = 10,
        alive_only: bool = False,
        origin: Union[UserOrigin, str] = UserOrigin.LOCAL,
        sort_key: Union[
            UserSortKey,
            str,
        ] = UserSortKey.FOLLOWER,
        sort_asc: bool = False,
    ) -> List[dict]:
        """Get list of users that include the specified hashtag in their
        profile.

        Args:
            tag (str): Specifies the hashtag to search.

            limit (int, default: :code:`10`): Specifies the amount to get.
            You can specify from 1 to 100.

            alive_only (bool, default: :code:`False`): Specifies whether to
            only get users active in 5 days.

            origin (str, default: :code:`local`): Specifies the origin type of
            users to get. Available values are enumerated in
            :class:`enum.UserOrigin`. If :code:`combined`, both :code:`local`
            and :code:`remote` users are included in the result.

            sort_key (str, default: :code:`follower`):
            Specifies sort key. Available values are enumerated in
            :class:`enum.UserSortKey`.

            sort_asc (bool, default: :code:`False`): Specifies the sort order.
            Hashtags sort in ascending order according to the key specified
            with :obj:`sort_key` if :code:`True`, descending order if
            :code:`False`.

        Endpoint:
            :code:`hashtags/users`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of users.

        Raises:
            MisskeyAPIException: Raise if the API request fails.

            ValueError: Raise if :code:`origin` or :code:`sort_key` is invalid.
        """
        state = 'alive' if alive_only else 'all'
        if type(origin) is str:
            origin = UserOrigin(origin)
        if type(sort_key) is str:
            sort_key = UserSortKey(sort_key)
        sort = '-' if sort_asc else '+'
        sort += sort_key.value
        del alive_only, sort_key, sort_asc
        params = self.__params(locals())
        return self.__request_api('hashtags/users', **params)

    def pages_create(
        self,
        title: str,
        name: str,
        summary: Optional[str] = None,
        content: List[dict] = [],
        variables: List[dict] = [],
        script: str = '',
        eye_catching_image_id: Optional[str] = None,
        font_serif: bool = False,
        align_center: bool = False,
        hide_title_when_pinned: bool = False,
    ) -> dict:
        """Create a page.

        Args:
            title (str): Specifies the title of the page.

            name (str): Specifies the unique name of the page.

            summary (str, optional): Specifies the summary of the page.

            content (:obj:`list` of :obj:`dict`): Specifies the content of the
            page.

            variables (:obj:`list` of :obj:`dict`): Specifies the variables
            that are to be used in the page.

            script (str): Specifies the script that is used in the page.

            eye_catching_image_id (str, optional): Specifies the file ID of the
            eye catching image of the page.

            font_serif (bool, default: :code:`False`): Specifies the font. If
            :code:`True`, serif and if :code:`False`. sans-serif.

            align_center (bool, default: :code:`False`): Specifies whether to
            center contents of the page.

            hide_title_when_pinned (bool, default: :code:`False`): Specifies
            whether to hide title when pinned to the profile.

        Endpoint:
            :code:`pages/create`

        Returns:
            dict: Returns the created page information.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        font = 'serif' if font_serif else 'sans-serif'
        params = self.__params(locals(), ('font_serif',))
        return self.__request_api('pages/create', **params)

    def pages_delete(
        self,
        page_id: str
    ) -> bool:
        """Delete a page.

        Args:
            page_id (str): Specifies the page ID.

        Endpoint:
            :code:`pages/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('pages/delete', pageId=page_id)

    def pages_featured(self) -> List[dict]:
        """Get a list of featured pages.

        Endpoint:
            :code:`pages/featured`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of most liked pages.
            No more than 10 pages are in the list.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('pages/featured')

    def pages_like(
        self,
        page_id: str
    ) -> bool:
        """Give a like to a page.

        Args:
            page_id (str): Specifies the page ID.

        Endpoint:
            :code:`pages/like`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('pages/like', pageId=page_id)

    def pages_show(
        self,
        page_id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> dict:
        """Get information of the specified page.

        Args:
            page_id (str, optional): Specifies the page ID.

            name (str, optional): Specifies the unique name of the page.

            username (str, optional): Specifies the username of the page
            author.

        Endpoint:
            :code:`pages/show`

        Returns:
            dict: Returns the page information.

        Note:
            You must specify either :code:`page_id` or :code:`name`.

            If you specify :code:`name`, you must specify :code:`username`.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('pages/show', **params)

    def pages_unlike(
        self,
        page_id: str
    ) -> bool:
        """Remove a like to the note.

        Args:
            page_id (str): Specifies the page ID.

        Endpoint:
            :code:`pages/unlike`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('pages/unlike', **params)

    def pages_update(
        self,
        page_id: str,
        title: str,
        name: str,
        summary: Optional[str] = None,
        content: List[dict] = [],
        variables: List[dict] = [],
        script: str = '',
        eye_catching_image_id: Optional[str] = None,
        font_serif: bool = False,
        align_center: bool = False,
        hide_title_when_pinned: bool = False,
    ) -> bool:
        """Update a page.

        Args:
            page_id (str): Specifies the page ID to update.

            title (str): Specifies the title of the page.

            name (str): Specifies the unique name of the page.

            summary (str, optional): Specifies the summary of the page.

            content (:obj:`list` of :obj:`dict`): Specifies the content of the
            page.

            variables (:obj:`list` of :obj:`dict`): Specifies the variables
            that are to be used in the page.

            script (str): Specifies the script that is used in the page.

            eye_catching_image_id (str, optional): Specifies the file ID of the
            eye catching image of the page.

            font_serif (bool, default: :code:`False`): Specifies the font. If
            :code:`True`, serif and if :code:`False`. sans-serif.

            align_center (bool, default: :code:`False`): Specifies whether to
            center contents of the page.

            hide_title_when_pinned (bool, default: :code:`False`): Specifies
            whether to hide title when pinned to the profile.

        Endpoint:
            :code:`pages/update`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Note:
            If you do not specify any of arguments, the corresponding parts of
            your page settings will be updated with the default values.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('pages/update', **params)
