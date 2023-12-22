from .notes import Misskey as NotesMisskey
from .i import Misskey as MeMisskey
from .meta import Misskey as MetaMisskey
from .users import Misskey as UsersMisskey
from .drive import Misskey as DriveMisskey
from .misc import Misskey as MiscMisskey
from .notifications import Misskey as NotificationsMisskey

__all__ = (
    "Misskey",
)


class Misskey(
    NotesMisskey,
    MeMisskey,
    MetaMisskey,
    UsersMisskey,
    DriveMisskey,
    MiscMisskey,
    NotificationsMisskey,
):
    pass
