import uuid
from typing import Union


class MisskeyAPIException(Exception):
    __code: str
    __id: Union[uuid.UUID, str]
    __message: str

    @property
    def code(self):
        return self.__code

    @property
    def id(self):
        return self.__id

    @property
    def message(self):
        return self.__message

    def __init__(self, response_dict: dict):
        if response_dict.get('error') is not None:
            self.__code = response_dict['error']['code']
            self.__message = response_dict['error']['message']
            try:
                self.__id = uuid.UUID(response_dict['error']['id'])
            except (ValueError, TypeError):
                self.__id = response_dict['error']['id']


class MisskeyAuthorizeFailedException(Exception):
    pass
