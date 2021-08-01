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
    Any
)
from urllib.parse import urlparse

import requests

from .enum import (
    NoteVisibility,
    NotificationsType
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
    ):
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
            Tuple[Union[NotificationsType, str]],
            Set[NotificationsType],
            None,
        ] = None,
        exclude_types: Union[
            List[Union[NotificationsType, str]],
            Tuple[Union[NotificationsType, str]],
            Set[NotificationsType],
            None,
        ] = None,
    ) -> List[dict]:
        if type(include_types) is list or type(include_types) is tuple:
            for index, val in enumerate(include_types):
                if type(val) is str:
                    include_types[index] = NotificationsType(val)

        if type(exclude_types) is list or type(include_types) is tuple:
            for index, val in enumerate(exclude_types):
                if type(val) is str:
                    exclude_types[index] = NotificationsType(val)

        params = self.__params(locals())
        return self.__request_api('i/notifications', **params)

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
