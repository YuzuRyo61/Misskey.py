import uuid
from urllib.parse import urlencode
from typing import Optional, List


__all__ = (
    "MiAuthBase",
)


class MiAuthBase(object):
    address: str
    session_id: str
    name: str
    callback: Optional[str] = None
    permission: Optional[List[str]] = None

    @staticmethod
    def __add_protocol(address: str) -> str:
        if (not address.startswith("http://") and not
           address.startswith("https://")):
            address = "https://" + address

        address.rstrip("/")
        return address

    def __init__(
        self, *,
        address: str,
        session_id: Optional[str] = None,
        name: str,
        icon: Optional[str] = None,
        callback: Optional[str] = None,
        # TODO: Enumerate permissions
        permission: Optional[List[str]] = None,
    ):
        self.name = name
        self.address = self.__add_protocol(address)
        self.icon = icon
        self.callback = callback
        self.permission = permission
        if session_id is None:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id

    def generate_url(self):
        query = {
            "name": self.name,
        }
        if self.icon is not None:
            query["icon"] = self.icon
        if self.callback is not None:
            query["callback"] = self.callback
        if self.permission is not None:
            query["permission"] = ",".join(self.permission)

        return f"{self.address}/miauth/{self.session_id}?{urlencode(query)}"

    def auth(self):
        # Define MiAuth HTTP processing in subclasses
        raise NotImplementedError()
