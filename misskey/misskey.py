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
    __DEFAULT_ADDRESS: str = 'https://misskey.io'

    __address: str
    __scheme: str
    __session: requests.Session

    __token: Optional[str] = None
    timeout: Optional[Any] = 15.0

    @property
    def address(self):
        return self.__address

    @property
    def __api_url(self):
        return f'{self.__scheme}://{self.__address}/api'

    @property
    def token(self):
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
        return self.__request_api('i')

    def meta(
        self,
        detail: bool = True,
    ) -> dict:
        return self.__request_api('meta', detail=detail)

    def stats(self) -> dict:
        return self.__request_api('stats')

    def announcements(
        self,
        limit: int = 10,
        with_unreads: bool = True,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('announcements', **params)

    def i_favorites(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        param = self.__params(locals())

        return self.__request_api('i/favorites', **param)

    def i_pin(
        self,
        note_id: str,
    ) -> dict:
        return self.__request_api('i/pin', noteId=note_id)

    def i_unpin(
        self,
        note_id: str,
    ) -> dict:
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
        return self.__request_api('notes/show', noteId=note_id)

    def notes_conversation(
        self,
        note_id: str,
        limit: int = 10,
        offset: Optional[int] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('notes/conversation', **params)

    def notes_children(
        self,
        note_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('notes/children', **params)

    def notes_replies(
        self,
        note_id: str,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('notes/replies', **params)

    def notes_renotes(
        self,
        note_id: str,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('notes/renotes', **params)

    def notes_unrenote(
        self,
        note_id: str
    ) -> bool:
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
        params = self.__params(locals())
        return self.__request_api('notes/reactions/create', **params)

    def notes_reactions_delete(
        self,
        note_id: str,
    ) -> bool:
        params = self.__params(locals())
        return self.__request_api('notes/reactions/delete', **params)

    def notes_polls_vote(
        self,
        note_id: str,
        choice: int,
    ) -> bool:
        return self.__request_api(
            'notes/polls/vote',
            noteId=note_id,
            choice=choice,
        )

    def notes_state(
        self,
        note_id: str,
    ) -> dict:
        return self.__request_api(
            'notes/state',
            noteId=note_id,
        )

    def notes_favorites_create(
        self,
        note_id: str,
    ) -> bool:
        return self.__request_api(
            'notes/favorites/create',
            noteId=note_id,
        )

    def notes_favorites_delete(
        self,
        note_id: str,
    ) -> bool:
        return self.__request_api(
            'notes/favorites/delete',
            noteId=note_id,
        )

    def notes_watching_create(
        self,
        note_id: str,
    ) -> bool:
        return self.__request_api(
            'notes/watching/create',
            noteId=note_id,
        )

    def notes_watching_delete(
        self,
        note_id: str,
    ) -> bool:
        return self.__request_api(
            'notes/watching/delete',
            noteId=note_id,
        )

    def notes_delete(
        self,
        note_id: str,
    ) -> bool:
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
        params = self.__params(locals())
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
        params = self.__params(locals())
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
        with_files: bool = True,
        file_type: Optional[List[str]] = None,
        exclude_nsfw: bool = False,
    ) -> List[dict]:
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
        return self.__request_api('users/stats', userId=user_id)

    def users_relation(
        self,
        user_id: Union[str, List[str]],
    ) -> Union[dict, List[dict]]:
        return self.__request_api('users/relation', userId=user_id)

    def users_lists_create(
        self,
        name: str,
    ) -> dict:
        return self.__request_api('users/lists/create', name=name)

    def users_lists_list(self) -> List[dict]:
        return self.__request_api('users/lists/list')

    def users_lists_show(
        self,
        list_id: str,
    ) -> dict:
        return self.__request_api('users/lists/show', listId=list_id)

    def users_lists_push(
        self,
        list_id: str,
        user_id: str,
    ) -> bool:
        params = self.__params(locals())
        return self.__request_api('users/lists/push', **params)

    def users_lists_pull(
        self,
        list_id: str,
        user_id: str,
    ) -> bool:
        params = self.__params(locals())
        return self.__request_api('users/lists/pull', **params)

    def users_lists_update(
        self,
        list_id: str,
        name: str,
    ) -> dict:
        params = self.__params(locals())
        return self.__request_api('users/lists/update', **params)

    def users_lists_delete(
        self,
        list_id: str,
    ) -> bool:
        return self.__request_api('users/lists/delete', listId=list_id)

    def users_report_abuse(
        self,
        user_id: str,
        comment: str,
    ) -> bool:
        params = self.__params(locals())
        return self.__request_api('users/report-abuse', **params)

    def following_create(
        self,
        user_id: str,
    ) -> dict:
        return self.__request_api('following/create', userId=user_id)

    def following_delete(
        self,
        user_id: str,
    ) -> dict:
        return self.__request_api('following/delete', userId=user_id)

    def mute_create(
        self,
        user_id: str,
    ) -> bool:
        return self.__request_api('mute/create', userId=user_id)

    def mute_list(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('mute/list', **params)

    def mute_delete(
        self,
        user_id: str,
    ) -> bool:
        return self.__request_api('mute/delete', userId=user_id)

    def blocking_create(
        self,
        user_id: str,
    ) -> dict:
        return self.__request_api('blocking/create', userId=user_id)

    def blocking_list(
        self,
        limit: int = 30,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('blocking/list', **params)

    def blocking_delete(
        self,
        user_id: str,
    ) -> dict:
        return self.__request_api('blocking/delete', userId=user_id)

    def following_requests_accept(
        self,
        user_id: str,
    ) -> bool:
        return self.__request_api(
            'following/requests/accept',
            userId=user_id
        )

    def following_requests_reject(
        self,
        user_id: str,
    ) -> bool:
        return self.__request_api(
            'following/requests/reject',
            userId=user_id,
        )

    def following_requests_cancel(
        self,
        user_id: str,
    ) -> dict:
        return self.__request_api(
            'following/requests/cancel',
            userId=user_id,
        )

    def following_requests_list(
        self,
    ) -> List[dict]:
        return self.__request_api('following/requests/list')

    def drive(self) -> dict:
        return self.__request_api('drive')

    def drive_stream(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> List[dict]:
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
        return self.__request_api('drive/files/check-existence', md5=md5)

    def drive_files_attached_notes(
        self,
        file_id: str,
    ) -> List[dict]:
        return self.__request_api(
            'drive/files/attached-notes',
            fileId=file_id
        )

    def drive_files_find_by_hash(
        self,
        md5: str,
    ) -> List[dict]:
        return self.__request_api(
            'drive/files/find-by-hash',
            md5=md5,
        )

    def drive_files_show(
        self,
        file_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> dict:
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
        return self.__request_api('drive/files/delete', fileId=file_id)

    def drive_folders(
        self,
        limit: int = 10,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> List[dict]:
        params = self.__params(locals())
        return self.__request_api('drive/folders', **params)

    def drive_folders_create(
        self,
        name: str = 'Untitled',
        parent_id: Optional[str] = None,
    ) -> dict:
        params = self.__params(locals())
        return self.__request_api('drive/folders/create', **params)

    def drive_folders_show(
        self,
        folder_id: str,
    ) -> dict:
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
        params = self.__params(locals(), {'parent_id'})
        if parent_id != '':
            params['parentId'] = parent_id
        return self.__request_api('drive/folders/update', **params)

    def drive_folders_delete(
        self,
        folder_id: str,
    ) -> bool:
        return self.__request_api(
            'drive/folders/delete',
            folderId=folder_id
        )
