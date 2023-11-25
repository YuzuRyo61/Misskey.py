from .notes import Misskey as NotesMisskey
from .i import Misskey as MeMisskey
from .meta import Misskey as MetaMisskey

__all__ = (
    "Misskey",
)


class Misskey(
    NotesMisskey,
    MeMisskey,
    MetaMisskey,
):
    pass
