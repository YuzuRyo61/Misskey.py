# -*- coding: utf-8 -*-
from json.decoder import JSONDecodeError
import json

class MisskeyAiException(Exception):
    """
    Raised if the specified function requires a token and no token is assigned to the class.
    """
    def __str__(self):
        return('APIToken(I) variable was undefined. Please set "self.apiToken" variable.')

class MisskeyFileException(Exception):
    """
    Raised when the specified file can not be found.
    """
    def __init__(self, filePath):
        self.filePath = filePath

    def __str__(self):
        return(f"File not found (or directory specified): {self.filePath}")

class MisskeyAPIException(Exception):
    """
    Raised if the API returns a status code that each function does not expect.
    """
    def __init__(self, apiName, exceptedCode, resCode, rawResponse):
        self.apiName = apiName
        self.exceptedCode = exceptedCode
        self.resCode = resCode
        self.rawResponse = rawResponse
        try:
            self.response = json.loads(rawResponse)['error']
        except JSONDecodeError:
            self.response = None
    
    def __str__(self):
        return(f'API Error: {self.apiName} (Expected value {self.exceptedCode}, but {self.resCode} returned)')

    def get_summary(self):
        return {
            'apiName': self.apiName,
            'exceptedCode': self.exceptedCode,
            'resCode': self.resCode,
            'rawResponse': self.rawResponse,
            'response': self.response
        }

class MisskeyInitException(MisskeyAPIException):
    """
    This exception is raised if an error occurs during class initialization. For example, it is raised if it can not connect to the specified address or if the token is invalid.
    """
    pass
