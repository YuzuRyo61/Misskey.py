from urllib.parse import urlparse

from typing import Optional, Any

__all__ = (
    "BaseMisskey",
)


class BaseMisskey(object):
    """
    This is the top-level Misskey class common to both synchronous and
    asynchronous processing.
    It defines properties and methods that are commonly handled.
    Since it is defined as a base class, this class does not operate by itself.
    """

    _address: str
    _token: Optional[str] = None

    @property
    def address(self) -> str:
        return self._address

    @property
    def token(self) -> Optional[str]:
        return self._token

    def __init__(
        self, *,
        address: str,
        token: Optional[str] = None,
    ):
        self._address = self._address_parse(address)

        self._token = token

    @staticmethod
    def _address_parse(address: str) -> str:
        parsed_address = urlparse(address)
        if parsed_address.scheme == "":
            parsed_address = urlparse(f"https://{address}")

        if (parsed_address.scheme != "http" and
           parsed_address.scheme != "https"):
            raise ValueError(
                f'Address protocol does not support "{parsed_address.scheme}"')

        return parsed_address._replace(
            path="",
            params="",
            query="",
            fragment="",
        ).geturl().rstrip("/")

    def _api_request(
        self, *,
        endpoint: str,
        params: Optional[dict] = None,
        **kwargs
    ) -> Any:
        raise NotImplementedError()
