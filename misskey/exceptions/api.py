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

    def __str__(self):
        return f"{self.code}({self.id}): {self.message}"

    @classmethod
    def from_dict(cls, data: dict):
        if "error" not in data.keys():
            raise TypeError("Not in the form of an error response")
        elif type(data["error"]) is not dict:
            raise TypeError("key 'error' is not dict")
        return cls(
            id=data["error"].get("id", str(uuid.UUID(int=0))),
            code=data["error"].get("code", "UNKNOWN"),
            message=data["error"].get("message", ""),
        )
