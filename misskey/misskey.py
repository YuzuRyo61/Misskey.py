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
)
from urllib.parse import urlparse

import requests

from .enum import (
    NoteVisibility,
    NotificationsType,
    LangType,
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
        fields: Optional[List[dict]] = None,
        is_locked: Optional[bool] = None,
        is_explorable: Optional[bool] = None,
        hide_online_status: Optional[bool] = None,
        careful_bot: Optional[bool] = None,
        auto_accept_followed: Optional[bool] = None,
        no_crawle: Optional[bool] = None,
        is_bot: Optional[bool] = None,
        is_cat: Optional[bool] = None,
        inject_featured_note: Optional[bool] = None,
        receive_announcement_email: Optional[bool] = None,
        always_mark_nsfw: Optional[bool] = None,
        pinned_page_id: Optional[str] = None,
        muted_words: Optional[List[List[str]]] = None,
        muting_notification_types: Union[
            List[Union[NotificationsType, str]],
            Tuple[NotificationsType],
            Set[NotificationsType],
            None,
        ] = None,
        email_notification_types: Optional[List[str]] = None,
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

            fields (:obj:`list` of :obj:`dict`, optional):
            Profile supplementary information.

            is_locked (:obj:`bool`, optional): Whether to make
            follow-up approval system.

            is_explorable (:obj:`bool`, optional): Whether to set as
            a discoverable user.

            hide_online_status (:obj:`bool`, optional): Whether to
            hide online status.

            careful_bot (:obj:`bool`, optional): Whether to
            approve follow-ups from bots.

            auto_accept_followed (:obj:`bool`, optional): Whether to
            automatically follow from the users you are following

            no_crawle (:obj:`bool`, optional): Specifies whether to
            prevent it from being tracked by search engines.

            is_bot (:obj:`bool`, optional): Whether to operate as a bot.

            is_cat (:obj:`bool`, optional): Specifies whether to use nyaise.

            inject_featured_note (:obj:`bool`, optional):

            receive_announcement_email (:obj:`bool`, optional):

            always_mark_nsfw (:obj:`bool`, optional): Whether to give NSFW
            to the posted file by default.

            pinned_page_id (:obj:`str`, optional): ID of the page to be fixed.

            muted_words (:obj:`list` of :obj:`list` of :obj:`str`, optional):
            Word to mute.

            muting_notification_types (:obj:`list`, optional):
            Notification type to hide.

            email_notification_types (:obj:`list` of :obj:`str`, optional):
            Specify the notification type for email notification.

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

        if type(muting_notification_types) is list:
            for index, val in enumerate(muting_notification_types):
                if type(val) is str:
                    muting_notification_types[index] = NotificationsType(val)

        params = self.__params(locals())
        return self.__request_api('i/update', **params)

    def notes_create(
        self,
        text: Optional[str] = None,
        cw: Optional[str] = None,
        visibility: Union[NoteVisibility, str] = NoteVisibility.PUBLIC,
        visible_user_ids: Optional[List[str]] = None,
        via_mobile: bool = False,
        local_only: bool = False,
        no_extract_mentions: bool = False,
        no_extract_hashtags: bool = False,
        no_extract_emojis: bool = False,
        file_ids: Optional[List[str]] = None,
        reply_id: Optional[str] = None,
        renote_id: Optional[str] = None,
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

            via_mobile (:obj:`bool`, optional): Specify whether to post from
            mobile. It doesn't work with recent Misskey versions.

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

            offset (int, optional): Specify the offset to get.

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

            offset (int, optional): Specify the offset to get.

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

    def notes_watching_create(
        self,
        note_id: str,
    ) -> bool:
        """Watch a note.

        Args:
            note_id (str): Specify the Note ID to watch.

        Endpoint:
            :code:`notes/watching/create`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'notes/watching/create',
            noteId=note_id,
        )

    def notes_watching_delete(
        self,
        note_id: str,
    ) -> bool:
        """Unwatch a note.

        Args:
            note_id (str): Specify the Note ID to unwatch.

        Endpoint:
            :code:`notes/watching/delete`

        Returns:
            bool: Returns :code:`True` if the request was successful.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api(
            'notes/watching/delete',
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
        with_files: bool = True,
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

            with_files (bool, optional): Specify whether to include files.

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
        with_files: bool = True,
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

            with_files (bool, optional): Specify whether to include files.

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
        with_files: bool = True,
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

            with_files (bool, optional): Specify whether to include files.

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
        with_files: bool = True,
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

            with_files (bool, optional): Specify whether to include files.

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
            :code:`users/report/abuse`

        Returns:
            bool: Returns :code:`True` if the report is sent.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        params = self.__params(locals())
        return self.__request_api('users/report-abuse', **params)

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

    def mute_create(
        self,
        user_id: str,
    ) -> bool:
        """Mute the specified user.

        Args:
            user_id (str): Specify the user ID.

        Endpoint:
            :code:`mute/create`

        Returns:
            bool: Returns :code:`True` if the user is muted.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
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
    ) -> List[dict]:
        """Get list of following requests.

        Endpoint:
            :code:`following/requests/list`

        Returns:
            :obj:`list` of :obj:`dict`: Returns the list of following requests.

        Raises:
            MisskeyAPIException: Raise if the API request fails.
        """
        return self.__request_api('following/requests/list')

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
