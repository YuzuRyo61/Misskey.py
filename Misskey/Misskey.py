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
        
        :param address: Instance address of Misskey. If leave a blank, library will use 'misskey.io'.
        :param i: Use hashed keys or keys used on the web.
        :param skipChk: Skip instance valid check. It is not recommended to make it True.
        :raises MisskeyInitException: This exception is raised if an error occurs during class initialization. For example, it is raised if it can not connect to the specified address or if the token is invalid.
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

        :noindex:
        :raises MisskeyAPIException:
        :raises MisskeyAiException:
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

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :type limit: int
        :type sinceId: str
        :type untilId: str
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

        :param text: It is an argument of the text.
        :param cw: If set, this argument will be displayed in the main on the timeline.
        :param visibility: Specify the open range.
        :param visibleUserIds: When "specified" is specified, if the user ID is put in this argument, the user can view the post.
        :param viaMobile: Mark it as posted as mobile if you set it to True.
        :param localOnly: You can specify whether to post only locally.
        :param noExtractMentions: Specify whether to not expand mentions from the text.
        :param noExtractHashtags: Specifies whether to not expand the hash tag from the text.
        :param noExtractEmojis: Specify whether to not extract custom pictograms from the text.
        :param fileIds: You can specify the file ID attached to the post.
        :param replyId: Specify the noteID to reply.
        :param renoteId: Specify the note ID to be Renote.
        :param poll: Designate when voting. You can specify 2 to 10 items.
        :param pollMultiple: Specifies whether to allow multiple votes.
        :param pollExpiresAt: Specifies the time to expire. If pollExpiresAt and pollExpiresAfter are not specified, it will be a vote indefinitely.
        :param pollExpiredAfter: Specify the specified period from the post. If pollExpiresAt and pollExpiresAfter are not specified, it will be a vote indefinitely.
        :type text: str or None
        :type cw: str or None
        :type visibility: str
        :type visibleUserIds: list
        :type viaMobile: bool
        :type localOnly: bool
        :type noExtractMentions: bool
        :type noExtractHashtags: bool
        :type noExtractEmojis: bool
        :type fileIds: list
        :type replyId: str or None
        :type renoteId: str or None
        :type poll: list
        :type pollMultiple: bool
        :type pollExpiresAt: str or None
        :type pollExpiredAfter: str or None
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
        Support fucntion: Renote a note (If use quote renote, please use `notes_create`)

        :param noteId: Specify the note ID you want to Renote.
        :type noteId: str
        :rtype: dict
        """
        return self.__API('notes/create', True, renoteId=noteId)

    def notes_renotes(self, noteId, limit=10, sinceId=None, untilId=None):
        """
        Show renote lists from note.

        :param noteId: Specify the noteID for which you want to check the details.
        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :type noteId: str
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
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

        :param noteId: Specify the note ID you want to delete.
        :type noteId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('notes/delete', True, 204, noteId=noteId)

    def notes_show(self, noteId):
        """
        Show a note.

        :param noteId: Specify the noteID to display details.
        :type noteId: str
        :rtype: dict
        """
        return self.__API('notes/show', True, noteId=noteId)

    def notes_reactions_create(self, noteId, reaction):
        """
        Give a reaction for note.

        :param noteId: Specify the noteID to which you want a reaction.
        :param reaction: Specify the type of reaction.
        :type noteId: str
        :type reaction: int or str
        :return: Returns `True` if the request is successful.
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

        :param noteId: Designate note ID for removing reaction.
        :type noteId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('notes/reactions/delete', True, 204, noteId=noteId)
    
    def notes_polls_vote(self, noteId, choice):
        """
        Vote a note.

        :param noteId: Specify the note ID of the vote. The specified noteID must have a voting attribute.
        :param choice: Select the item to vote.
        :type noteId: str
        :type choice: int
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('notes/polls/vote', True, 204, noteId=noteId, choice=choice)

    def notes_favorites_create(self, noteId):
        """
        Mark as favorite to note.

        :param noteId: Specify the note ID to register the favorite.
        :type noteId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('notes/favorites/create', True, 204, noteId=noteId)

    def notes_favorites_delete(self, noteId):
        """
        Remove mark favorite to note.

        :param noteId: Specify noteID to remove the favorite.
        :type noteId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('notes/favorites/delete', True, 204, noteId=noteId)

    def notes_globalTimeline(self, withFiles=False, limit=10, sinceId=None, untilId=None, sinceDate=None, untilDate=None):
        """
        Show timeline from Global.

        :param withFiles: If True, only posts attached to the file will be displayed.
        :param excludeNsfw: Set to True to exclude postings for reading attention.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceDate: Get from the specified date.
        :param untilDate: Gets until the specified date.
        :type withFiles: bool
        :type excludeNsfw: bool
        :type sinceId: str or None
        :type untilId: str or None
        :type limit: int
        :type sinceDate: str or None
        :type untilDate: str or None
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

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param sinceDate: Get from the specified date.
        :param untilDate: Gets until the specified date.
        :param withFiles: If True, only posts attached to the file will be displayed.
        :param includeMyRenotes: Specify if you want to include posts that you renote
        :param includeRenotedMyNotes: Specifies whether your post includes a Renote post
        :param includeLocalRenotes: Specifies whether to include reposted local posts
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
        :type sinceDate: str or None
        :type untilDate: str or None
        :type withFiles: bool
        :type includeMyRenotes: bool
        :type includeRenotedMyNotes: bool
        :type includeLocalRenotes: bool
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

        :param withFiles: If True, only posts attached to the file will be displayed.
        :param fileType: Use when acquiring only the specified file type.
        :param excludeNsfw: Set to True to exclude postings for reading attention.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceDate: Get from the specified date.
        :param untilDate: Gets until the specified date.
        :type withFiles: bool
        :type fileType: list or None
        :type excludeNsfw: bool
        :type sinceId: str or None
        :type untilId: str or None
        :type limit: int
        :type sinceDate: str or None
        :type untilDate: str or None
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
        If userIds specify a username, this function will return a `list` type.

        :param userId: It is an argument used when acquiring a single user. It can not be used in conjunction with userIds.
        :param userIds: It is an argument used when acquiring multiple users. It can not be used in combination with userId.
        :param username: It is an argument that can use the user name displayed in the instance. This is useful when you do not know the user ID.
        :param host: Used to get the user of another instance.
        :type userId: str or None
        :type userIds: str or None
        :type username: str or None
        :type host: str or None
        :rtype: dict, list
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

        :param userId: Specify the user ID to display the follower list.
        :param username: Specify the user name for displaying the follower list. This is useful when you do not know the user ID.
        :param host: Used to load the user of another instance.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param limit: Maximum number to get. You can specify from 1 to 100.
        :type userId: str or None
        :type username: str or None
        :type host: str or None
        :type sinceId: str or None
        :type untilId: str or None
        :type limit: int
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

        :param userId: Specify the user ID for displaying the follow list.
        :param username: Specify the user name for displaying the follow list. This is useful when you do not know the user ID.
        :param host: Used to load the user of another instance.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param limit: Maximum number to get. You can specify from 1 to 100.
        :type userId: str or None
        :type username: str or None
        :type host: str or None
        :type sinceId: str or None
        :type untilId: str or None
        :type limit: int
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

        :param userId: Specify the user ID to follow.
        :type userId: str
        :rtype: dict
        """
        return self.__API('following/create', True, 200, userId=userId)
    
    def following_delete(self, userId):
        """
        Unfollow a user.

        :param userId: Specify the user ID to unfollow.
        :type userId: str
        :rtype: dict
        """
        return self.__API('following/delete', True, 200, userId=userId)

    def mute_create(self, userId):
        """
        Mute a user.

        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('mute/create', True, 204, userId=userId)

    def mute_list(self, limit=30, sinceId=None, untilId=None):
        """
        List blocked users.

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
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

        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('mute/delete', True, 204, userId=userId)

    def blocking_create(self, userId):
        """
        Block a user.

        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('blocking/create', True, 200, userId=userId)

    def blocking_list(self, limit=30, sinceId=None, untilId=None):
        """
        List blocked users.

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
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

        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('blocking/delete', True, 200, userId=userId)

    def drive(self):
        """
        Show your capacity.
        
        :rtype: dict
        """
        return self.__API('drive', True)

    def drive_files(self, limit=10, sinceId=None, untilId=None, folderId="", type=None):
        """
        Show a files in selected folder.

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param folderId: You can specify a folder ID to refer to.
        :param type: Specifies the file type.
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
        :type folderId: str or None
        :type type: str or None
        :rtype: list
        """
        payload = {
            'limit': limit
        }
        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        if folderId != "": # pragma: no cover
            payload['folderId'] = folderId

        if type != None: # pragma: no cover
            payload['type'] = type

        return self.__API('drive/files', True, 200, **payload)

    def drive_files_create(self, filePath, folderId=None, isSensitive=False, force=False):
        """
        Upload a file.

        :param filePath: Specify the path where the file is located.
        :param folderId: If specified, it will be uploaded to that folder.
        :param isSensitive: Specify whether to upload as browsing notice.
        :param force: Specify whether to force even if a file with the same hash is uploaded.
        :type folderId: str or None
        :type isSensitive: bool
        :type force: bool
        :raises MisskeyFileException: Raised if the file can not be found.
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

        :param url: Specify the URL to upload to the drive.
        :param folderId: If specified, it will be uploaded to that folder.
        :param isSensitive: Specify whether to upload as browsing notice.
        :param force: Specify whether to force even if a file with the same hash is uploaded.
        :type url: str
        :type folderId: str or None
        :type isSensitive: bool
        :type force: bool
        :rtype: dict
        """
        return self.__API('drive/files/upload-from-url', True, 200, url=url, folderId=folderId, isSensitive=isSensitive, force=force)

    def drive_files_show(self, fileId=None, url=None):
        """
        Show a file from fileID or URL.

        :param fileId: Specify the file ID for which you want to check the details
        :param url: Enter the URL uploaded to the drive of the instance for which you want to check the details. This is useful when you do not know the file ID.
        :type fileId: str or None
        :type url: str or None
        :rtype: dict
        """
        payload = {}

        if fileId != None: # pragma: no cover
            payload['fileId'] = fileId

        if url != None: # pragma: no cover
            payload['url'] = url
        
        return self.__API('drive/files/show', True, 200, **payload)
    
    def drive_files_update(self, fileId, folderId="", name=None, isSensitive=None):
        """
        Update a file.

        :param fileId: Specify the file ID you want to change
        :param folderId: If specified, it will move to that folder.
        :param name: Change to the file name entered in the argument.
        :param isSensitive: You can change whether to set to reading attention.
        :type fileId: str
        :type folderId: str or None
        :type name: str or None
        :type isSensitive: bool or None
        :rtype: dict
        """
        payload = {
            'fileId': fileId
        }

        if folderId != "": # pragma: no cover
            payload['folderId'] = folderId

        if name != None: # pragma: no cover
            payload['name'] = name

        if isSensitive != None: # pragma: no cover
            payload['isSensitive'] = isSensitive
        
        return self.__API('drive/files/update', True, 200, **payload)

    def drive_files_delete(self, fileId):
        """
        Delete a file.

        :param fileId: Specify the file ID you want to delete.
        :type fileId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('drive/files/delete', True, 204, fileId=fileId)
    
    def drive_folders(self, limit=10, sinceId=None, untilId=None, folderId=None):
        """
        List folders in specified directory.

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param folderId: You can specify a folder ID to refer to.
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
        :type folderId: str or None
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

        :param name: Enter the folder ID you want to create
        :param parentId: Specify where to create the folder. If not specified, it will be created in the root folder.
        :type name: str
        :type parentId: str or None
        :rtype: dict
        """
        return self.__API('drive/folders/create', True, 200, name=name, parentId=parentId)

    def drive_folders_show(self, folderId):
        """
        Show a folder.

        :param folderId: Enter the folder ID for which you want to check the details
        :type folderId: str
        :rtype: dict
        """
        return self.__API('drive/folders/show', True, 200, folderId=folderId)

    def drive_folders_update(self, folderId, name=None, parentId=""):
        """
        Update a folder.

        :param folderId: Enter the folder ID you want to update
        :param name: Enter in this argument when you want to change it.
        :param parentId: Change this argument if you want to change the parent folder.
        :type folderId: str
        :type name: str or None
        :type parentId: str or None
        :rtype: dict
        """
        payload = {
            'folderId': folderId
        }

        if name != None: # pragma: no cover
            payload['name'] = name

        if parentId != "": # pragma: no cover
            payload['parentId'] = parentId
        
        return self.__API('drive/folders/update', True, 200, **payload)

    def drive_folders_delete(self, folderId):
        """
        Delete a folder in specified directory.

        :param folderId: Enter the folder ID you want to delete
        :type folderId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('drive/folders/delete', True, 204, folderId=folderId)

    def messaging_history(self, limit=10):
        """
        Show all messages what you received.

        :param limit: Maximum number to get. You can specify from 1 to 100.
        :type limit: int
        :rtype: list
        """
        return self.__API('messaging/history', True, 200, limit=limit)

    def messaging_messages(self, userId, limit=10, sinceId=None, untilId=None, markAsRead=True):
        """
        Show messages.

        :param userId: Display a message with the specified user.
        :param limit: Maximum number to get. You can specify from 1 to 100.
        :param sinceId: Acquired from the specified ID.
        :param untilId: Get up to the specified ID.
        :param markAsRead: You can choose to mark unread messages as read when you call this API.
        :type userId: str
        :type limit: int
        :type sinceId: str or None
        :type untilId: str or None
        :type markAsRead: bool
        :rtype: list
        """
        payload = {
            'userId': userId,
            'limit': limit,
            'markAsRead': markAsRead
        }

        if sinceId != None: # pragma: no cover
            payload['sinceId'] = sinceId
        
        if untilId != None: # pragma: no cover
            payload['untilId'] = untilId
        
        return self.__API('messaging/messages', True, 200, **payload)

    def messaging_messages_create(self, userId, text=None, fileId=None):
        """
        Send a message to a specified user.

        :param userId: Sends a message to the specified user.
        :param text: Insert the text to be sent.
        :param fileId: If you want to attach a file, enter the file ID.
        :type userId: str
        :type text: str or None
        :type fileId: str or None
        :rtype: dict
        """
        payload = {
            'userId': userId
        }

        if text != None: # pragma: no cover
            payload['text'] = text
        
        if fileId != None: # pragma: no cover
            payload['fileId'] = fileId
        
        return self.__API('messaging/messages/create', True, 200, **payload)

    def messaging_messages_delete(self, messageId):
        """
        Deletes the specified message.

        :param messageId: Enter the unique ID of the sent message.
        :type messageId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('messaging/messages/delete', True, 204, messageId=messageId)

    def messaging_messages_read(self, messageId):
        """
        Mark the specified message as read.

        :param messageId: Enter the unique ID of the sent message.
        :type messageId: str
        :return: Returns `True` if the request is successful.
        :rtype: bool
        """
        return self.__API('messaging/messages/read', True, 204, messageId=messageId)
