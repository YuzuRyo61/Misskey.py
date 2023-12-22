import datetime
from typing import TypedDict, List, Optional

__all__ = (
    "PollCreateDict",
)


class PollCreateDict(TypedDict):
    choices: List[str]
    multiple: Optional[bool]
    expires_at: Optional[datetime.datetime]
    expired_after: Optional[int]
