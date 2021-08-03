import uuid
from typing import Union


class MisskeyAPIException(Exception):
    __code: str
    __id: Union[uuid.UUID, str]
    __message: str

    @property
    def code(self) -> str:
        return self.__code

    @property
    def id(self) -> Union[uuid.UUID, str]:
        return self.__id

    @property
    def message(self) -> str:
        return self.__message

    def __init__(self, response_dict: dict):
        if response_dict.get('error') is not None:
            self.__code = response_dict['error']['code']
            self.__message = response_dict['error']['message']
            try:
                self.__id = uuid.UUID(response_dict['error']['id'])
            except (ValueError, TypeError):
                self.__id = str(response_dict['error']['id'])
        else:
            self.__code = 'UNKNOWN'
            self.__message = 'Unknown exception in Misskey.py'
            self.__id = uuid.UUID(int=0)

    def __str__(self) -> str:
        return f'{self.__code}({self.__id}): {self.__message}'


class MisskeyAuthorizeFailedException(Exception):
    pass


class MisskeyMiAuthFailedException(Exception):
    pass
