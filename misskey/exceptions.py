import uuid
from typing import Union


class MisskeyAPIException(Exception):
    __code: str = 'UNKNOWN'
    __id: Union[uuid.UUID, str] = uuid.UUID(int=0)
    __message: str = 'Unknown exception in Misskey.py'

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
            self.__code = response_dict['error'].get('code', self.__code)
            self.__message = response_dict['error'].get(
                'message', self.__message)
            try:
                self.__id = uuid.UUID(str(response_dict['error'].get(
                    'id', self.__id)))
            except (ValueError, TypeError):
                self.__id = str(response_dict['error'].get('id', self.__id))

    def __str__(self) -> str:
        return f'{self.__code}({self.__id}): {self.__message}'


class MisskeyAuthorizeFailedException(Exception):
    pass


class MisskeyMiAuthFailedException(Exception):
    pass
