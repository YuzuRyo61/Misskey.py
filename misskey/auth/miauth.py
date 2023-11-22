from typing import Optional

import requests

from .miauth_base import MiAuthBase
from ..schemas import (
    MiAuthResult,
    MiAuthResultSchema,
)

__all__ = (
    "MiAuth",
)


class MiAuth(MiAuthBase):
    session: requests.Session

    def __init__(
        self, *,
        session: Optional[requests.Session] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if session is not None:
            self.session = session
        else:
            self.session = requests.Session()

    def auth(self) -> MiAuthResult:
        result_raw = requests.post(
            f"{self.address}/api/miauth/{self.session_id}/check")
        result_raw.raise_for_status()
        return MiAuthResultSchema().load(result_raw.json())
