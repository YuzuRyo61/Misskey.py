# -*- coding: utf-8 -*-

from Misskey.Exceptions import MisskeyInitException, MisskeyAPIException, MisskeyAiException

import requests
import json
import hashlib
from urllib.parse import urlparse

class Misskey:
    def __init__(self, address='misskey.xyz', apiToken=None, skipChk=False):
        """
        Initialize the library.
        
        :param address: Instance address of Misskey. If leave a blank, library will use 'misskey.xyz'.
        :param apiToken: Known as "I". Use hashed keys or keys used on the web.
        :param skipChk: Skip instance valid check. It is not recommended to make it True.
        """
        self.headers = {'content-type': 'application/json'}
        self.apiToken = apiToken

        ParseRes = urlparse(address)
        if ParseRes.scheme == '':
            ParseRes = urlparse(f"https://{address}")
        self.address = ParseRes.netloc
        self.instanceAddressApiUrl = f"{ParseRes.scheme}://{ParseRes.netloc}/api"

        if not skipChk:
            res = requests.post(self.instanceAddressApiUrl + '/meta')
            if res.status_code != 200:
                raise MisskeyInitException('API Error: /meta')
            if apiToken != None:
                res = requests.post(self.instanceAddressApiUrl + '/i', data=json.dumps({'i': apiToken}), headers=self.headers)
                if res.status_code != 200:
                    raise MisskeyInitException('API Authorize Error: /i')

    def __API(self, apiName, includeI=False, expected=200, **payload):
        if includeI:
            if self.apiToken != None:
                payload['i'] = self.apiToken
            else:
                raise MisskeyAiException('apiToken variable was undefined. Please set apiToken variable.')
        
        res = requests.post(self.instanceAddressApiUrl + apiName, data=json.dumps(payload), headers=self.headers)

        if res.status_code != expected:
            raise MisskeyAPIException(f'API Error: {apiName} (Expected value {expected}, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    def meta(self):
        return self.__API('/meta')

    def stats(self):
        return self.__API('/stats')

    def notes_create(
        self,
        text=None,
        cw=None,
        visibility="public",
        visibleUserIds=[],
        viaMobile=False,
        localOnly=False,
        noExtractMentions=False,
        noExtractHashtags=False,
        noExtractEmojis=False,
        fileIds=[],
        replyId=None,
        renoteId=None,
        pollChoices=[],
        pollMultiple=False
    ):
        payload = {
            'visibility': visibility,
            'text': text,
            'cw': cw,
            'viaMobile': viaMobile,
            'localOnly': localOnly,
            'noExtractMentions': noExtractMentions,
            'noExtractHashtags': noExtractHashtags,
            'noExtractEmojis': noExtractEmojis
        }

        if visibility == 'specified':
            payload['visibleUserIds'] = visibleUserIds

        if fileIds != []:
            payload['fileIds'] = fileIds

        if replyId != None:
            payload['replyId'] = replyId

        if renoteId != None:
            payload['renoteId'] = renoteId

        if pollChoices != []:
            payload['poll']['choices'] = pollChoices
            payload['poll']['multiple'] = pollMultiple
        
        return self.__API('/notes/create', True, 200, **payload)