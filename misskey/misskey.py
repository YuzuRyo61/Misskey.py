from typing import Optional
from urllib.parse import urlparse

import requests

from .exceptions import MisskeyAuthorizeFailedException


class Misskey:
    __DEFAULT_ADDRESS: str = 'https://misskey.io'

    __address: str
    __scheme: str
    __session: requests.Session

    __token: Optional[str] = None

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
        )
        if credential_res.status_code == 403 or \
           credential_res.status_code == 401:
            raise MisskeyAuthorizeFailedException()

        self.__token = new_token
        return

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
            body['i'] = i

        meta_res = self.__session.post(
            f'{self.__api_url}/meta',
            json=body,
            allow_redirects=False
        )

        if meta_res.status_code == 403:
            raise MisskeyAuthorizeFailedException()
