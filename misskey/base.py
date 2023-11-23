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

    address: str
    token: Optional[str] = None

    def __init__(
        self, *,
        address: str,
        token: Optional[str] = None,
    ):
        self.address = self._add_protocol(address)

        self.token = token

    @staticmethod
    def _add_protocol(address: str) -> str:
        if (not address.startswith("http://") and not
           address.startswith("https://")):
            address = "https://" + address

        address.rstrip("/")
        return address

    def _api_request(
        self, *,
        endpoint: str,
        params: Optional[dict] = None,
        **kwargs
    ) -> Any:
        raise NotImplementedError()
