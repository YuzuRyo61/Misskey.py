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

    def i_favorites(self, limit=10, sinceId=None, untilId=None):
        """
        Show your favorite notes.
        :rtype: list
        """
        payload = {
            'limit': limit
        }
        
        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        return self.__API('i/favorites', True, 200, **payload)

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

        if visibility == 'specified': # pragma: no cover
            payload['visibleUserIds'] = visibleUserIds

        if fileIds != []: # pragma: no cover
            payload['fileIds'] = fileIds

        if replyId != None: # pragma: no cover
            payload['replyId'] = replyId

        if renoteId != None: # pragma: no cover
            payload['renoteId'] = renoteId

        if poll != []: # pragma: no cover
            payload['poll'] = {}
            payload['poll']['choices'] = poll
            payload['poll']['multiple'] = pollMultiple
            if pollExpiresAt != None:
                payload['poll']['expiresAt'] = pollExpiresAt
            if pollExpiredAfter != None:
                payload['poll']['expiredAfter'] = pollExpiredAfter
        
        return self.__API('notes/create', True, 200, **payload)

    def notes_renote(self, noteId): # pragma: no cover
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

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId

        if untilId != None: # pragma: no cover
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
        if type(reaction) == int and (reaction >= 0 and reaction <= 9): # pragma: no cover
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
        else: # pragma: no cover
            payload['reaction'] = reaction
        
        return self.__API('notes/reactions/create', True, 204, **payload)
    
    def notes_reactions_delete(self, noteId):
        """
        Cancel a reaction for note.
        :rtype: bool
        """
        return self.__API('notes/reactions/delete', True, 204, noteId=noteId)
    
    def notes_polls_vote(self, noteId, choice):
        """
        Vote a note.
        :rtype: bool
        """
        return self.__API('notes/polls/vote', True, 204, noteId=noteId, choice=choice)

    def notes_favorites_create(self, noteId):
        """
        Mark as favorite to note.
        :rtype: bool
        """
        return self.__API('notes/favorites/create', True, 204, noteId=noteId)

    def notes_favorites_delete(self, noteId):
        """
        Remove mark favorite to note.
        :rtype: bool
        """
        return self.__API('notes/favorites/delete', True, 204, noteId=noteId)

    def notes_globalTimeline(self, withFiles=False, limit=10, sinceId=None, untilId=None, sinceDate=None, untilDate=None):
        """
        Show timeline from Global.
        :rtype: list
        """
        payload = {
            'withFiles': withFiles,
            'limit': limit
        }

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId

        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        if sinceDate != None: # pragma: no cover
            payload['sinceDate'] = sinceDate

        if untilDate != None: # pragma: no cover
            payload['untilDate'] = untilDate
        
        return self.__API('notes/global-timeline', False, 200, **payload)

    def notes_hybridTimeline(
            self,
            limit=10,
            sinceId=None,
            untilId=None,
            sinceDate=None,
            untilDate=None,
            includeMyRenotes=True,
            includeRenotedMyNotes=True,
            includeLocalRenotes=True,
            withFiles=False):
        """
        Show timeline from Hybrid(Social).
        :rtype: list
        """
        payload = {
            'limit': limit,
            'includeMyRenotes': includeMyRenotes,
            'includeRenotedMyNotes': includeRenotedMyNotes,
            'includeLocalRenotes': includeLocalRenotes,
            'withFiles': withFiles
        }

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId

        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        if sinceDate != None: # pragma: no cover
            payload['sinceDate'] = sinceDate

        if untilDate != None: # pragma: no cover
            payload['untilDate'] = untilDate

        return self.__API('notes/hybrid-timeline', True, 200, **payload)

    def notes_localTimeline(self, withFiles=False, fileType=None, excludeNsfw=False, limit=10, sinceId=None, untilId=None, sinceDate=None, untilDate=None):
        """
        Show timeline from Local.
        :rtype: list
        """
        payload = {
            'withFiles': withFiles,
            'limit': limit
        }

        if fileType != None: # pragma: no cover
            payload['fileType'] = fileType
            payload['excludeNsfw'] = excludeNsfw

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId

        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        if sinceDate != None: # pragma: no cover
            payload['sinceDate'] = sinceDate

        if untilDate != None: # pragma: no cover
            payload['untilDate'] = untilDate
        
        return self.__API('notes/local-timeline', False, 200, **payload)

    def users_show(self, userId=None, userIds=None, username=None, host=None):
        """
        Show user(s).
        :rtype: dict
        :rtype: list
        """
        payload = {}
        
        if userId != None: # pragma: no cover
            payload['userId'] = userId
        
        if userIds != None and type(userIds) == list: # pragma: no cover
            payload['userIds'] = userIds

        if username != None: # pragma: no cover
            payload['username'] = username

        if host != None: # pragma: no cover
            payload['host'] = host
        
        return self.__API('users/show', False, 200, **payload)
    
    def users_followers(self, userId=None, username=None, host=None, sinceId=None, untilId=None, limit=10):
        """
        Show followers from specified user.
        :rtype: list
        """
        payload = {
            'limit': limit
        }

        if userId != None: # pragma: no cover
            payload['userId'] = userId
        
        if username != None: # pragma: no cover
            payload['username'] = username

        if host != None: # pragma: no cover
            payload['host'] = host

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId

        return self.__API('users/followers', False, 200, **payload)
    
    def users_following(self, userId=None, username=None, host=None, sinceId=None, untilId=None, limit=10):
        """
        Show following from specified user.
        :rtype: list
        """
        payload = {
            'limit': limit
        }

        if userId != None: # pragma: no cover
            payload['userId'] = userId
        
        if username != None: # pragma: no cover
            payload['username'] = username

        if host != None: # pragma: no cover
            payload['host'] = host

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId

        return self.__API('users/following', False, 200, **payload)

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

    def mute_create(self, userId):
        """
        Mute a user.
        :rtype: dict
        """
        return self.__API('mute/create', True, 204, userId=userId)

    def mute_list(self, limit=30, sinceId=None, untilId=None):
        """
        List blocked users.
        :rtype: list
        """
        payload = {
            'limit': limit
        }

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId

        return self.__API('mute/list', True, 200, **payload)

    def mute_delete(self, userId):
        """
        Unmute a user.
        :rtype: bool
        """
        return self.__API('mute/delete', True, 204, userId=userId)

    def blocking_create(self, userId):
        """
        Block a user.
        :rtype: bool
        """
        return self.__API('blocking/create', True, 200, userId=userId)

    def blocking_list(self, limit=30, sinceId=None, untilId=None):
        """
        List blocked users.
        :rtype: list
        """
        payload = {
            'limit': limit
        }

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId

        return self.__API('blocking/list', True, 200, **payload)

    def blocking_delete(self, userId):
        """
        Unblock a user.
        :rtype: bool
        """
        return self.__API('blocking/delete', True, 200, userId=userId)

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
        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        if folderId != None: # pragma: no cover
            payload['folderId'] = folderId

        if type != None: # pragma: no cover
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

        if res.status_code != 200: # pragma: no cover
            raise MisskeyAPIException(f'API Error: drive/files/create (Expected value 200, but {res.status_code} returned)\n{res.text}')
        else:
            return json.loads(res.text)

    def drive_files_uploadFromUrl(self, url, folderId=None, isSensitive=False, force=False):
        """
        Upload a file from URL.
        :rtype: dict
        """
        return self.__API('drive/files/upload-from-url', True, 200, url=url, folderId=folderId, isSensitive=isSensitive, force=force)

    def drive_files_show(self, fileId=None, url=None):
        """
        Show a file from fileID or URL.
        :rtype: dict
        """
        payload = {}

        if fileId != None: # pragma: no cover
            payload['fileId'] = fileId

        if url != None: # pragma: no cover
            payload['url'] = url
        
        return self.__API('drive/files/show', True, 200, **payload)
    
    def drive_files_update(self, fileId, folderId=None, name=None, isSensitive=None):
        """
        Update a file.
        :rtype: dict
        """
        payload = {
            'fileId': fileId,
            'folderId': folderId
        }

        if name != None: # pragma: no cover
            payload['name'] = name

        if isSensitive != None: # pragma: no cover
            payload['isSensitive'] = isSensitive
        
        return self.__API('drive/files/update', True, 200, **payload)

    def drive_files_delete(self, fileId):
        """
        Delete a file.
        :rtype: bool
        """
        return self.__API('drive/files/delete', True, 204, fileId=fileId)
    
    def drive_folders(self, limit=10, sinceId=None, untilId=None, folderId=None):
        """
        List folders in specified directory.
        :rtype: list
        """
        payload = {
            'limit': limit,
            'folderId': folderId
        }
        
        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        return self.__API('drive/folders', True, 200, **payload)

    def drive_folders_create(self, name="Untitled", parentId=None):
        """
        Create a folder in specified directory.
        :rtype: dict
        """
        return self.__API('drive/folders/create', True, 200, name=name, parentId=parentId)

    def drive_folders_show(self, folderId):
        """
        Show a folder.
        :rtype: dict
        """
        return self.__API('drive/folders/show', True, 200, folderId=folderId)

    def drive_folders_update(self, folderId, name=None, parentId=None):
        """
        Update a folder.
        :rtype: dict
        """
        payload = {
            'folderId': folderId
        }

        if name != None: # pragma: no cover
            payload['name'] = name

        if parentId != None: # pragma: no cover
            payload['parentId'] = parentId
        
        return self.__API('drive/folders/update', True, 200, **payload)

    def drive_folders_delete(self, folderId):
        """
        Delete a folder in specified directory.
        :rtype: bool
        """
        return self.__API('drive/folders/delete', True, 204, folderId=folderId)
