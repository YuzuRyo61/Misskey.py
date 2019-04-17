# -*- coding: utf-8 -*-

from Misskey.Exceptions import MisskeyInitException, MisskeyAPIException, MisskeyAiException, MisskeyFileException

import requests
import json
import os
import mimetypes
from urllib.parse import urlparse

class Misskey:
    def __init__(self, address='misskey.io', i=None, skipChk=False):
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
        self.instanceAddressApiUrl = f"{ParseRes.scheme}://{ParseRes.netloc}/api/"

        if not skipChk:
            res = requests.post(self.instanceAddressApiUrl + 'meta')
            if res.status_code != 200:
                raise MisskeyInitException(f'API Error: meta\n{res.text}')
            if i != None:
                res = requests.post(self.instanceAddressApiUrl + 'i', data=json.dumps({'i': i}), headers=self.headers)
                if res.status_code != 200:
                    raise MisskeyInitException(f'API Authorize Error: i\n{res.text}')

    def __API(self, apiName, includeI=False, expected=200, **payload):
        """
        This function is for internal. Normally, Please use each functions.
        """
        if includeI:
            if self.apiToken != None:
                payload['i'] = self.apiToken
            else:
                raise MisskeyAiException('APIToken(I) variable was undefined. Please set "apiToken" variable.')
        
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
        :rtype: dict
        """
        return self.__API('meta')

    def stats(self):
        """
        Read a instance stats information.
        :rtype: dict
        """
        return self.__API('stats')

    def i(self):
        """
        Show your credential.
        :rtype: dict
        """
        return self.__API('i', True)

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
        poll=[],
        pollMultiple=False,
        pollExpiresAt=None,
        pollExpiredAfter=None
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

        if poll != []:
            payload['poll'] = {}
            payload['poll']['choices'] = poll
            payload['poll']['multiple'] = pollMultiple
            if pollExpiresAt != None:
                payload['poll']['expiresAt'] = pollExpiresAt
            if pollExpiredAfter != None:
                payload['poll']['expiredAfter'] = pollExpiredAfter
        
        return self.__API('notes/create', True, 200, **payload)

    def notes_renote(self, noteId):
        """
        Support fucntion: Renote a note (If use quote renote, please use notes_create)
        :rtype: dict
        """
        return self.__API('notes/create', True, renoteId=noteId)

    def notes_renotes(self, noteId, limit=10, sinceId=None, untilId=None):
        """
        Show renote lists from note.
        :rtype: list
        """
        payload = {
            'noteId': noteId,
            'limit': limit
        }

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['untilId'] = untilId
        
        return self.__API('notes/renotes', False, 200, **payload)
    
    def notes_delete(self, noteId):
        """
        Delete a own note.
        :rtype: bool
        """
        return self.__API('notes/delete', True, 204, noteId=noteId)

    def notes_show(self, noteId):
        """
        Show a note.
        :rtype: dict
        """
        return self.__API('notes/show', True, noteId=noteId)

    def notes_reactions_create(self, noteId, reaction):
        """
        Give a reaction for note.
        :rtype: bool
        """
        payload = {
            'noteId': noteId
        }
        if type(reaction) == int and (reaction >= 0 and reaction <= 9):
            reactionTemplate = (
                'pudding',
                'like',
                'love',
                'laugh',
                'hmm',
                'surprise',
                'congrats',
                'angry',
                'confused',
                'rip'
            )
            payload['reaction'] = reactionTemplate[reaction]
        else:
            payload['reaction'] = reaction
        
        return self.__API('notes/reactions/create', True, 204, **payload)
    
    def notes_reactions_delete(self, noteId):
        """
        Cancel a reaction for note.
        :rtype: bool
        """
        return self.__API('notes/reactions/delete', True, 204, noteId=noteId)

    def users_show(self, userId=None, userIds=None, username=None, host=None):
        """
        Show user(s).
        :rtype: dict
        :rtype: list
        """
        payload = {}
        
        if userId != None:
            payload['userId'] = userId
        
        if userIds != None and type(userIds) == list:
            payload['userIds'] = userIds

        if username != None:
            payload['username'] = username

        if host != None:
            payload['host'] = host
        
        return self.__API('users/show', True, 200, **payload)

    def following_create(self, userId):
        """
        Follow a user.
        :rtype: dict
        """
        return self.__API('following/create', True, 200, userId=userId)
    
    def following_delete(self, userId):
        """
        Unfollow a user.
        :rtype: dict
        """
        return self.__API('following/delete', True, 200, userId=userId)

    def drive(self):
        """
        Show your capacity.
        :rtype: dict
        """
        return self.__API('drive', True)

    def drive_files(self, limit=10, sinceId=None, untilId=None, folderId=None, type=None):
        """
        Show a files in selected folder.
        :rtype: list
        """
        payload = {
            'limit': limit
        }
        if sinceId != None:
            payload['sinceId'] = sinceId
        
        if untilId != None:
            payload['untilId'] = untilId
        
        if folderId != None:
            payload['folderId'] = folderId

        if type != None:
            payload['type'] = type

        return self.__API('drive/files', True, 200, **payload)

    def drive_files_create(self, filePath, folderId=None, isSensitive=False, force=False):
        """
        Upload a file.
        :rtype: dict
        """
        if not os.path.isfile(filePath):
            raise MisskeyFileException(f"File not found (or directory specified): {filePath}")
        
        fileName = os.path.basename(filePath)
        fileAbs = os.path.abspath(filePath)
        fileBin = open(fileAbs, 'rb')
        fileMime = mimetypes.guess_type(fileAbs)

        filePayload = {'file': (fileName, fileBin, fileMime[0])}
        payload = {'i': self.apiToken, 'folderId': folderId, 'isSensitive': isSensitive, 'force': force}

        res = requests.post(self.instanceAddressApiUrl + "drive/files/create", data=payload, files=filePayload)
        fileBin.close()

        if res.status_code != 200:
            raise MisskeyAPIException(f'API Error: drive/files/create (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    def drive_files_uploadFromUrl(self, url, folderId=None, isSensitive=False, force=False):
        """
        Upload a file from URL.
        :rtype: dict
        """
        return self.__API('drive/files/upload-from-url', True, 200, url=url, folderId=folderId, isSensitive=isSensitive, force=force)
    
    def drive_files_delete(self, fileId):
        """
        Delete a file.
        :rtype: bool
        """
        return self.__API('drive/files/delete', True, 204, fileId=fileId)