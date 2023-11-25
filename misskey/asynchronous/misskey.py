from .i import AsyncMisskey as MeAsyncMisskey
from .notes import AsyncMisskey as NotesAsyncMisskey

__all__ = (
    "AsyncMisskey",
)


class AsyncMisskey(
    MeAsyncMisskey,
    NotesAsyncMisskey,
):
    """
    This class allows asynchronous processing and manipulation
    of Misskey's API using aiohttp.
    If the "async" extra is not given when installing the
    Misskey.py library, it may not work properly.
    """
    pass
