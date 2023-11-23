import uuid
from urllib.parse import urlencode
from typing import Optional, List, Union

from ..enum import MisskeyPermissionEnum
from ..schemas import MiAuthResult


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
        permission: Optional[
            Union[List[str], List[MisskeyPermissionEnum]]] = None,
    ):
        self.name = name
        self.address = self.__add_protocol(address)
        self.icon = icon
        self.callback = callback
        if session_id is None:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id

        if permission is not None:
            perm = []
            for p in permission:
                if type(p) is MisskeyPermissionEnum:
                    perm.append(p.value)
                elif type(p) is str:
                    perm.append(p)
            self.permission = perm

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

    def auth(self, *args, **kwargs) -> MiAuthResult:
        # Define MiAuth HTTP processing in subclasses
        raise NotImplementedError()
