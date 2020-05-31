import hashlib
import json
import requests
import warnings
import functools
import uuid

from urllib.parse import urlparse, urlencode

from Misskey.Exceptions import (
    MisskeyAPIException,
    MisskeyInitException,
    MisskeyNotImplementedVersionException,
    MisskeyMiAuthCheckException
)
from Misskey import __version__

def deprecated(func): # pragma: no cover
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

@deprecated
def hash_apitoken(accessToken, appSecret): # pragma: no cover
    """
    **Deprecated**
    The issued access token and app secret key are combined and hashed for use in API.

    :param accessToken: Token Specify the access token issued at the time of authentication.
    :param appSecret: Specify the app secret key.
    :type accessToken: str
    :type appSecret: str
    :rtype: str
    """
    tokenraw = accessToken + appSecret
    return hashlib.sha256(tokenraw.encode('utf-8')).hexdigest()

@deprecated
def create_app(instanceAddress, appName, description, permission=[
    'read:account',
    'write:account',
    'read:blocks',
    'write:blocks',
    'read:drive',
    'write:drive',
    'read:favorites',
    'write:favorites',
    'read:following',
    'write:following',
    'read:messaging',
    'write:messaging',
    'read:mutes',
    'write:mutes',
    'write:notes',
    'read:notifications',
    'write:notifications',
    'read:reactions',
    'write:reactions',
    'write:votes'
], callbackUrl=None): # pragma: no cover
    """
    **Deprecated**
    Creates an application key with the specified instance address.

    :param instanceAddress: Specify the Misskey instance address.
    :param appName: Specifies the name of the app.
    :param description: Specify the app description.
    :param permission: Specifies the app's permissions.
    :param callbackUrl: Specify if there is a URL to call back after user authentication.
    :type instanceAddress: str
    :type appName: str
    :type description: str
    :type permission: list
    :type callbackUrl: str or None
    :rtype: dict
    """
    res = requests.post(f"https://{instanceAddress}/api/app/create", data=json.dumps({'name': appName, 'description': description, 'permission': permission, 'callbackUrl': callbackUrl}), headers={'content-type': 'application/json'})

    if res.status_code != 200:
        raise MisskeyAPIException('/app/create', 200, res.status_code, res.text)
    else:
        return json.loads(res.text)

@deprecated
def session_generate(instanceAddress, appSecret): # pragma: no cover
    """
    **Deprecated**
    Issue a token to authenticate the user.

    :param instanceAddress: Specify the Misskey instance address.
    :param appSecret: Specifies the secret key.
    :type instanceAddress: str
    :type appSecret: str
    :rtype: dict
    """
    res = requests.post(f"https://{instanceAddress}/api/auth/session/generate", data=json.dumps({'appSecret': appSecret}), headers={'content-type': 'application/json'})

    if res.status_code != 200:
        raise MisskeyAPIException('/auth/session/generate', 200, res.status_code, res.text)
    else:
        return json.loads(res.text)

@deprecated
def session_userkey(instanceAddress, appSecret, token): # pragma: no cover
    """
    **Deprecated**
    It is a function to perform when the user authenticates with the browser.

    :param instanceAddress: Specify the Misskey instance address.
    :param appSecret: Specifies the secret key.
    :param token: Specify the token issued before authentication.
    :type instanceAddress: str
    :type appSecret: str
    :type token: str
    :rtype: dict
    """
    res = requests.post(f"https://{instanceAddress}/api/auth/session/userkey", data=json.dumps({'appSecret': appSecret, 'token': token}), headers={'content-type': 'application/json'})

    if res.status_code != 200:
        raise MisskeyAPIException('/auth/session/userkey', 200, res.status_code, res.text)
    else:
        return json.loads(res.text)

def username_available(instanceAddress, username):
    """
    Checks if the specified user name can be used.

    :param instanceAddress: Specify the Misskey instance address.
    :param username: Specify the username you want to check.
    :type instanceAddress: str
    :type username: str
    :rtype: dict
    """
    res = requests.post(f"https://{instanceAddress}/api/username/available", data=json.dumps({'username': username,}), headers={'content-type': 'application/json'})

    if res.status_code != 200: # pragma: no cover
        raise MisskeyAPIException('/username/available', 200, res.status_code, res.text)
    else:
        return res.json()

class MiAuth: # pragma: no cover
    """
    Misskey authentication class
    """
    headers = {'content-type': 'application/json'}
    __token = None
    __user = None

    def __init__(
        self,
        instanceAddress="misskey.io",
        sessionId=uuid.uuid4,
        name=f"Misskey.py v{__version__}",
        icon=None,
        callback=None,
        permission=(
            "read:account",
            "write:account",
            "read:blocks",
            "write:blocks",
            "read:drive",
            "write:drive",
            "read:favorites",
            "write:favorites",
            "read:following",
            "write:following",
            "read:messaging",
            "write:messaging",
            "read:mutes",
            "write:mutes",
            "write:notes",
            "read:notifications",
            "write:notifications",
            "read:reactions",
            "write:reactions",
            "write:votes",
            "read:pages",
            "write:pages",
            "write:page-likes",
            "read:page-likes",
            "read:user-groups",
            "write:user-groups"
        )
    ):
        self.__instanceAddress = instanceAddress
        self.__sessionId = str(sessionId()) if sessionId == uuid.uuid4 else str(sessionId)
        self.__name = name
        self.__icon = icon
        self.__callback = callback
        self.__permission = permission

        ParseRes = urlparse(self.__instanceAddress)
        if ParseRes.scheme == '':
            ParseRes = urlparse(f"https://{self.__instanceAddress}")
        self.__address = ParseRes.netloc
        self.__instanceAddressUrl = f"{ParseRes.scheme}://{ParseRes.netloc}"

        res = requests.post(f"{ParseRes.scheme}://{ParseRes.netloc}/api/meta", headers=self.headers, allow_redirects=False)
        if res.status_code != 200:
            raise MisskeyInitException('meta', '200', res.status_code, res.text)
        else:
            if not res.json()["features"].get("miauth", False):
                raise MisskeyNotImplementedVersionException()

    @property
    def instanceAddress(self):
        return self.__instanceAddress
    
    @property
    def sessionId(self):
        return self.__sessionId

    @property
    def name(self):
        return self.__name
    
    @property
    def icon(self):
        return self.__icon
    
    @property
    def callback(self):
        return self.__callback
    
    @property
    def permission(self):
        return self.__permission
    
    @property
    def token(self):
        return self.__token
    
    @property
    def user(self):
        return self.__user

    def getUrl(self):
        payload = {
            "name": self.__name,
            "permission": ",".join(str(pq) for pq in self.__permission)
        }

        if self.__icon != None:
            payload["icon"] == self.__icon
        
        if self.__callback != None:
            payload["callback"] == self.__callback

        return f"{self.__instanceAddressUrl}/miauth/{self.__sessionId}?{urlencode(payload)}"

    def check(self):
        res = requests.post(f"{self.__instanceAddressUrl}/api/miauth/{self.__sessionId}/check")
        if res.status_code != 200: # pragma: no cover
            raise MisskeyAPIException(f'{self.__instanceAddressUrl}/api/miauth/{self.__sessionId}/check', 200, res.status_code, res.text)
        else:
            resj = res.json()
            if resj["ok"]:
                self.__token = resj["token"]
                self.__user = resj["user"]
                return resj
            else:
                raise MisskeyMiAuthCheckException()
