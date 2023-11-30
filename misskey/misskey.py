from .notes import Misskey as NotesMisskey
from .i import Misskey as MeMisskey
from .meta import Misskey as MetaMisskey
from .users import Misskey as UsersMisskey
from .misc import Misskey as MiscMisskey

__all__ = (
    "Misskey",
)


class Misskey(
    NotesMisskey,
    MeMisskey,
    MetaMisskey,
    UsersMisskey,
    MiscMisskey,
):
    pass
