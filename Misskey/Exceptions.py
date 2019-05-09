# -*- coding: utf-8 -*-

class MisskeyInitException(Exception):
    """
    This exception is raised if an error occurs during class initialization. For example, it is raised if it can not connect to the specified address or if the token is invalid.
    """
    pass

class MisskeyAPIException(Exception):
    """
    Raised if the API returns a status code that each function does not expect.
    """
    pass

class MisskeyAiException(Exception):
    """
    Raised if the specified function requires a token and no token is assigned to the class.
    """
    pass

class MisskeyFileException(Exception):
    """
    Raised when the specified file can not be found.
    """
    pass
