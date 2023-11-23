import copy
import requests
from typing import Optional, Any

from .base import BaseMisskey
from .exceptions import (
    MisskeyNetworkException,
    MisskeyIllegalArgumentError,
    MisskeyAPIException,
    MisskeyResponseError
)

__all__ = (
    "Misskey",
)


class Misskey(BaseMisskey):
    session: requests.Session

    def __init__(
        self, *,
        session: Optional[requests.Session] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

    def _api_request(
        self, *,
        endpoint: str,
        params: Optional[dict] = None,
        **kwargs
    ) -> Any:
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
            raise MisskeyNetworkException(f"Could not complete request: {e}")

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
