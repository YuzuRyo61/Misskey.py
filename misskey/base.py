import copy
from typing import Optional, Any

import requests

from .exceptions import (
    MisskeyNetworkException,
    MisskeyIllegalArgumentError,
    MisskeyResponseError,
    MisskeyAPIException,
)

__all__ = (
    "Misskey",
)


class Misskey(object):
    address: str
    token: Optional[str] = None
    session: requests.Session

    def __init__(
        self, *,
        address: str,
        token: Optional[str] = None,
        session: Optional[requests.Session] = None
    ):
        self.address = self.__add_protocol(address)

        self.token = token

        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

    @staticmethod
    def __add_protocol(address: str) -> str:
        if (not address.startswith("http://") and not
           address.startswith("https://")):
            address = "https://" + address

        address.rstrip("/")
        return address

    def __api_request(self, *, endpoint: str, params: dict = None) -> Any:
        if params is None:
            params = {}
        else:
            params = copy.deepcopy(params)

        if self.token is not None:
            params["i"] = self.token

        try:
            response_object = self.session.post(
                url=self.address + endpoint, json=params)
        except Exception as e:
            raise MisskeyNetworkException(f"Could not complete request: ${e}")

        if response_object is None:
            raise MisskeyIllegalArgumentError("Illegal response")

        try:
            response = response_object.json()

            if response_object.ok:
                return response
            else:
                raise MisskeyAPIException.from_dict(response)
        except requests.exceptions.JSONDecodeError:
            raise MisskeyResponseError("JSON decode error")
