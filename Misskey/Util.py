# -*- coding: utf-8 -*-
from Misskey.Exceptions import MisskeyAPIException

import hashlib
import json
import requests

class MisskeyUtil:
    @staticmethod
    def hash_apitoken(accessToken, appSecret):
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
        res = requests.post(f"https://{instanceAddress}/api/app/create", data=json.dumps({'name': appName, 'description': description, 'permission': permission, 'callbackUrl': callbackUrl}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /app/create (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def session_generate(instanceAddress, appSecret): # pragma: no cover
        res = requests.post(f"https://{instanceAddress}/api/auth/session/generate", data=json.dumps({'appSecret': appSecret}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /auth/session/generate (Expected value 200 but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def session_userkey(instanceAddress, appSecret, token): # pragma: no cover
        res = requests.post(f"https://{instanceAddress}/api/auth/session/userkey", data=json.dumps({'appSecret': appSecret, 'token': token}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /auth/session/userkey (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def username_available(instanceAddress, username):
        res = requests.post(f"https://{instanceAddress}/api/username/available", data=json.dumps({'username': username,}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /api/username/available (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)
