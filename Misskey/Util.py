# -*- coding: utf-8 -*-
from Misskey.Exceptions import MisskeyAPIException

import hashlib
import json
import requests

class MisskeyUtil:
    @staticmethod
    def hash_apitoken(accessToken, appSecret):
        """
        The issued access token and app secret key are combined and hashed for use in API.

        :param accessToken: Token Specify the access token issued at the time of authentication.
        :param appSecret: Specify the app secret key.
        :type accessToken: str
        :type appSecret: str
        :rtype: str
        """
        tokenraw = accessToken + appSecret
        return hashlib.sha256(tokenraw.encode('utf-8')).hexdigest()

    @staticmethod
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
            raise MisskeyAPIException(f'API Error: /app/create (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def session_generate(instanceAddress, appSecret): # pragma: no cover
        """
        Issue a token to authenticate the user.

        :param instanceAddress: Specify the Misskey instance address.
        :param appSecret: Specifies the secret key.
        :type instanceAddress: str
        :type appSecret: str
        :rtype: dict
        """
        res = requests.post(f"https://{instanceAddress}/api/auth/session/generate", data=json.dumps({'appSecret': appSecret}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /auth/session/generate (Expected value 200 but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def session_userkey(instanceAddress, appSecret, token): # pragma: no cover
        """
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
            raise MisskeyAPIException(f'API Error: /auth/session/userkey (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
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
            raise MisskeyAPIException(f'API Error: /api/username/available (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)
