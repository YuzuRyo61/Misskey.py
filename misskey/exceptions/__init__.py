from .api import (
    MisskeyAPIError,
)
from .network import (
    MisskeyNetworkError,
)


class MisskeyIllegalArgumentError(Exception):
    pass


class MisskeyResponseError(Exception):
    pass
