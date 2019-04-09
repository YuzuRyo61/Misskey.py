# -*- coding: utf-8 -*-

from Misskey.Exceptions import MisskeyInitException, MisskeyAPIException, MisskeyAiException

import requests
import json
import os
import mimetypes
from urllib.parse import urlparse

class Misskey:
    def __init__(self, address='misskey.xyz', i=None, skipChk=False):
        """
        Initialize the library.
        
        :param address: Instance address of Misskey. If leave a blank, library will use 'misskey.xyz'.
        :param i: Use hashed keys or keys used on the web.
        :param skipChk: Skip instance valid check. It is not recommended to make it True.
        """
        self.headers = {'content-type': 'application/json'}
        self.apiToken = i

        ParseRes = urlparse(address)
        if ParseRes.scheme == '':
            ParseRes = urlparse(f"https://{address}")
        self.address = ParseRes.netloc
        self.instanceAddressApiUrl = f"{ParseRes.scheme}://{ParseRes.netloc}/api"

        if not skipChk:
            res = requests.post(self.instanceAddressApiUrl + '/meta')
            if res.status_code != 200:
                raise MisskeyInitException('API Error: /meta')
            if i != None:
                res = requests.post(self.instanceAddressApiUrl + '/i', data=json.dumps({'i': i}), headers=self.headers)
                if res.status_code != 200:
                    raise MisskeyInitException('API Authorize Error: /i')

    def __API(self, apiName, includeI=False, expected=200, **payload):
        """
        This function is for internal. Normally, Please use each functions.
        """
        if includeI:
            if self.apiToken != None:
                payload['i'] = self.apiToken
            else:
                raise MisskeyAiException('apiToken variable was undefined. Please set apiToken variable.')
        
        res = requests.post(self.instanceAddressApiUrl + apiName, data=json.dumps(payload), headers=self.headers)

        if res.status_code != expected:
            raise MisskeyAPIException(f'API Error: {apiName} (Expected value {expected}, but {res.status_code} returned)\n{res.text}')
        else:
            if res.status_code == 204:
                return True
            else:
                return json.loads(res.text)

    def meta(self):
        """
        Read a instance meta information.
        :return: dict
        """
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
        """
        Post a new note.
        :rtype: dict
        """
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
    
    def notes_delete(self, noteId):
        """
        Delete a own note.
        :rtype: bool
        """
        return self.__API('/notes/delete', True, 204, noteId=noteId)

    def i(self):
        """
        Show your credential.
        :rtype: dict
        """
        return self.__API('/i', True)

    def drive_files_create(self, filePath, folderId=None, isSensitive=False, force=False):
        """
        Upload a file.
        :rtype: dict
        """
        fileName = os.path.basename(filePath)
        fileAbs = os.path.abspath(filePath)
        fileBin = open(fileAbs, 'rb')
        fileMime = mimetypes.guess_type(fileAbs)

        filePayload = {'file': (fileName, fileBin, fileMime[0])}
        payload = {'i': self.apiToken, 'folderId': folderId, 'isSensitive': isSensitive, 'force': force}

        res = requests.post(self.instanceAddressApiUrl + "/drive/files/create", data=payload, files=filePayload)
        fileBin.close()

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: /drive/files/create (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)