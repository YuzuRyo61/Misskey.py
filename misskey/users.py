from .sync_base import Misskey as Base

from typing import Optional, List, Union

from misskey.schemas import (
    MisskeyUser,
    # MisskeyUserSchema,
    MisskeyMeDetailed,
)

from misskey.schemas.arguments import (
    MisskeyNotesCreatePollSchema,
)
from misskey.exceptions import MisskeyResponseError

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def users_show(
        self, *,
        user_id: Optional[str] = None,
        user_ids: Optional[List[str]] = None,
        username: Optional[str] = None,
        host: Optional[str] = None,
    ) -> Union[
        MisskeyUser,
        MisskeyMeDetailed,
        List[Union[MisskeyUser, MisskeyMeDetailed]]
    ]:
        payload_dict = {}
        if user_id is not None:
            payload_dict["user_id"] = user_id
        if user_ids is not None:
            payload_dict["user_ids"] = user_ids
        if username is not None:
            payload_dict["username"] = username
            payload_dict["host"] = host

        payload = MisskeyNotesCreatePollSchema().dump(payload_dict)
        response = self._api_request(
            endpoint="/api/users/show", params=payload)

        if type(response) is list:
            # TODO: Return user information in list format
            pass
        elif type(response) is dict:
            # TODO: Allow to return standalone user information
            pass
        else:
            raise MisskeyResponseError("Illegal response type received")
