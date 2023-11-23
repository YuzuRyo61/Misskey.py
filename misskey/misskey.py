from .notes import Misskey as NotesMisskey
from .i import Misskey as MeMisskey

__all__ = (
    "Misskey",
)


class Misskey(
    NotesMisskey,
    MeMisskey,
):
    pass
