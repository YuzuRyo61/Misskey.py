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

TIME2000: datetime.datetime = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)

AID_REGEXP = re.compile(r"^[0-9a-z]{10}", flags=re.I)


class MisskeyAID(MisskeyID):
    aid_counter: int = int.from_bytes(
        secrets.token_bytes(2), byteorder="big")

    @staticmethod
    def get_time(*, t: datetime.datetime) -> str:
        # t's datetime timezone should be utc.
        time_counter: int = 0
        if t >= TIME2000:
            time_counter = math.floor((t - TIME2000).total_seconds() * 1000)

        return np.base_repr(time_counter, 36).zfill(8)

    @staticmethod
    def get_noise() -> str:
        # TODO: noise generator
        pass

    @classmethod
    def generate(cls, *, t: datetime.datetime):
        MisskeyAID.aid_counter += 1
        # TODO: generate id
        pass
