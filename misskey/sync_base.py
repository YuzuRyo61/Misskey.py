import copy
import requests
from typing import Optional, Any

from .base import BaseMisskey
from .exceptions import (
    MisskeyNetworkError,
    MisskeyIllegalArgumentError,
    MisskeyAPIError,
    MisskeyResponseError
)
from .enum import HttpMethodEnum

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
        method: HttpMethodEnum = HttpMethodEnum.POST,
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
            if method == HttpMethodEnum.GET:
                context = self.session.get(
                    url=self.address + endpoint)
            elif method == HttpMethodEnum.POST:
                context = self.session.post(
                    url=self.address + endpoint, json=params)
            else:
                raise NotImplementedError()
        except Exception as e:
            raise MisskeyNetworkError(f"Could not complete request: {e}")

        if context is None:
            raise MisskeyIllegalArgumentError("Illegal response")

        try:
            if (context.ok and
               context.status_code == requests.codes.no_content):
                # response is ok, but body is empty
                return

            response = context.json()

            if context.ok:
                return response
            else:
                raise MisskeyAPIError.from_dict(response)
        except requests.exceptions.JSONDecodeError:
            raise MisskeyResponseError("JSON decode error")
