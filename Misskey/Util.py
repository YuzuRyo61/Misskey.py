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
        'account-read',
        'account-write',
        'account/read',
        'account/write',
        'note-read',
        'note-write',
        'reaction-read',
        'reaction-write',
        'following-read',
        'following-write',
        'drive-read',
        'drive-write',
        'notification-read',
        'notification-write',
        'favorite-read',
        'favorites-read',
        'favorite-write',
        'messaging-read',
        'messaging-write',
        'vote-read',
        'vote-write'
    ], callbackUrl=None):
        res = requests.post(f"https://{instanceAddress}/api/app/create", data=json.dumps({'name': appName, 'description': description, 'permission': permission, 'callbackUrl': callbackUrl}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /app/create (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def session_generate(instanceAddress, appSecret):
        res = requests.post(f"https://{instanceAddress}/api/auth/session/generate", data=json.dumps({'appSecret': appSecret}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /auth/session/generate (Expected value 200 but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    @staticmethod
    def session_userkey(instanceAddress, appSecret, token):
        res = requests.post(f"https://{instanceAddress}/api/auth/session/userkey", data=json.dumps({'appSecret': appSecret, 'token': token}), headers={'content-type': 'application/json'})

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /auth/session/userkey (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)