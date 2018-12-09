# -*- coding: utf-8 -*-

class MisskeyInitException(Exception):
    pass

class MisskeyArgumentException(Exception):
    pass

class MisskeyBadRequestException(Exception):
    pass

class MisskeyIsntAdminException(Exception):
    pass

class MisskeyPermissionException(Exception):
    pass

class MisskeyForbiddenException(Exception):
    pass

class MisskeyResponseException(Exception):
    pass

class MisskeyWebSocketException(Exception):
    pass

class MisskeyUnknownException(Exception):
    pass
