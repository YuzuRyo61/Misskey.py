from .sync_base import Misskey as Base

from typing import Optional, List, Union

from misskey.schemas import (
    UserDetailed,
    UserDetailedSchema,
    MeDetailed,
    MeDetailedSchema,
)
from misskey.enum import (
    UsersSortEnum,
    UsersStateEnum,
    UsersOriginEnum,
)
from misskey.schemas.arguments import (
    UsersShowArgumentsSchema,
    UsersArgumentsSchema,
)
from misskey.exceptions import MisskeyResponseError

__all__ = (
    "Misskey",
)


class Misskey(Base):
    def users(
        self, *,
        limit: int = 10,
        offset: int = 0,
        sort: Optional[UsersSortEnum] = None,
        state: Optional[UsersStateEnum] = None,
        origin: UsersOriginEnum = UsersOriginEnum.LOCAL,
        hostname: Optional[str] = None,
    ) -> List[Union[UserDetailed, MeDetailed]]:
        payload_dict = {
            "limit": limit,
            "offset": offset,
            "hostname": hostname,
        }
        if sort is not None:
            payload_dict["sort"] = sort
        if state is not None:
            payload_dict["state"] = state
        if origin is not None:
            payload_dict["origin"] = origin

        payload = UsersArgumentsSchema().dump(payload_dict)
        response = self._api_request(
            endpoint="/api/users", params=payload)

        # TODO: Maybe there's a better way to identify them.
        return_data = []
        for res in response:
            if "avatarId" in response:
                return_data.append(MeDetailedSchema().load(res))
            else:
                return_data.append(UserDetailedSchema().load(res))
        return return_data

    def users_show(
        self, *,
        user_id: Optional[str] = None,
        user_ids: Optional[List[str]] = None,
        username: Optional[str] = None,
        host: Optional[str] = None,
    ) -> Union[
        UserDetailed,
        MeDetailed,
        List[Union[UserDetailed, MeDetailed]]
    ]:
        payload_dict = {}
        if user_id is not None:
            payload_dict["user_id"] = user_id
        if user_ids is not None:
            payload_dict["user_ids"] = user_ids
        if username is not None:
            payload_dict["username"] = username
            payload_dict["host"] = host

        payload = UsersShowArgumentsSchema().dump(payload_dict)
        response = self._api_request(
            endpoint="/api/users/show", params=payload)

        if type(response) is dict:
            # TODO: Maybe there's a better way to identify them.
            if "avatarId" in response:
                return MeDetailedSchema().load(response)
            else:
                return UserDetailedSchema().load(response)
        elif type(response) is list:
            # TODO: Maybe there's a better way to identify them.
            return_data = []
            for res in response:
                if "avatarId" in response:
                    return_data.append(MeDetailedSchema().load(res))
                else:
                    return_data.append(UserDetailedSchema().load(res))
            return return_data
        else:
            raise MisskeyResponseError("Illegal response type received")