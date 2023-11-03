import uuid

__all__ = (
    "MisskeyAPIException",
)


class MisskeyAPIException(Exception):
    id: str
    code: str
    message: str

    # noinspection PyShadowingBuiltins
    def __init__(self, *, id: str, code: str, message: str):
        self.id = id
        self.code = code
        self.message = message

    @classmethod
    def from_dict(cls, data: dict):
        if data.keys() not in ["error"]:
            raise TypeError("Not in the form of an error response")
        return cls(
            id=data["error"].get("id", str(uuid.UUID(int=0))),
            code=data["error"].get("code", "UNKNOWN"),
            message=data["error"].get("message", ""),
        )
