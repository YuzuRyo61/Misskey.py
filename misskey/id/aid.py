import datetime
import re
import secrets
import math
import numpy as np

from .base import MisskeyID

__all__ = (
    "MisskeyAID",
    "AID_REGEXP",
)

TIME2000_UTC: datetime.datetime = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)

AID_REGEXP = re.compile(r"^[0-9a-z]{10}", flags=re.I)


class MisskeyAID(MisskeyID):
    aid_counter: int = int.from_bytes(
        secrets.token_bytes(2), byteorder="big")  # Static

    def __init__(self, i: str):
        self.id = i

    # TODO: It would be better if IDs could be compared

    @staticmethod
    def get_time(*, t: datetime.datetime) -> str:
        # t's datetime timezone should be utc.
        time_counter: int = 0
        if t >= TIME2000_UTC:
            time_counter = math.floor((t - TIME2000_UTC).total_seconds() * 1000)

        return np.base_repr(time_counter, 36).zfill(8).lower()

    @staticmethod
    def get_noise() -> str:
        return np.base_repr(MisskeyAID.aid_counter, 36).zfill(2)[-2:].lower()

    @classmethod
    def generate(cls, *, t: datetime.datetime):
        MisskeyAID.aid_counter += 1
        return cls(cls.get_time(t=t) + cls.get_noise())

    def to_date(self) -> datetime.datetime:
        time = int(self.id[:-2], 36) / 1000
        return TIME2000_UTC + datetime.timedelta(seconds=time)
