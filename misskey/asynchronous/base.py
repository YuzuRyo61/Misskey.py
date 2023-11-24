import copy
import json
from typing import Optional, Any

import aiohttp

from misskey.base import BaseMisskey
from misskey.exceptions import (
    MisskeyAPIError,
    MisskeyNetworkError,
    MisskeyResponseError,
)


class AsyncMisskey(BaseMisskey):
    session: aiohttp.ClientSession

    def __init__(
        self, *,
        session: aiohttp.ClientSession,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.session = session

    async def _api_request(
        self, *,
        endpoint: str,
        params: Optional[dict] = None,
        **kwargs
    ) -> Any:
        if params is None:
            params = {}
        else:
            params = copy.deepcopy(params)

        if self.token is not None:
            params["i"] = self.token

        try:
            async with self.session.post(
                self.address + endpoint,
                headers={"Content-Type": "application/json"},
                json=params,
            ) as response_data:
                response = await response_data.json()
                if response_data.ok:
                    return response
                else:
                    raise MisskeyAPIError.from_dict(response)
        except json.JSONDecodeError:
            raise MisskeyResponseError("JSON decode error")
        except aiohttp.ContentTypeError as e:
            raise MisskeyNetworkError(f"Content-Type error: ${e}")
        except aiohttp.ClientError as e:
            raise MisskeyNetworkError(f"Could not complete request: {e}")
