# -*- coding: utf-8 -*-

from Misskey.Exceptions import *

import requests
import json
import pprint
import hashlib
import os
import mimetypes

from urllib.parse import urlparse

def isAdmin(isAdminFlag: bool):
    if isAdminFlag == False:
        raise MisskeyIsntAdminException("Using user is not Admin or Moderator!")

def construction(func):
    def _CONSTRUCTION_FUNCTION(*args, **kwargs):
        print("Sorry, This function is under construction.")
        return None
    return _CONSTRUCTION_FUNCTION


class Misskey:
    """
    MISSKEY API LIBRARY
    """
    def __init__(self, instanceAddress='https://misskey.xyz', appSecret=None, accessToken=None, apiToken=None):
        """
        INITIALIZE LIBRARY

        Attribute:
        * : Required
        - instanceAddress : Instance Address
        - appSecret : Application Secret Key
        - accessToken : accessToken key from authorized api
        - apiToken : sha256 hashed from appSecret and accessToken (If this is set, we will preferentially use this.)
        """
        self.instanceAddress = instanceAddress
        self.appSecret = appSecret
        self.accessToken = accessToken
        self.apiToken = apiToken

        self.headers = {'content-type': 'application/json'}
        self.metaDic = None
        self.credentials = None
        self.res = None
        self.i_isAdmin = False

        if self.apiToken == None and self.appSecret != None and self.accessToken != None:
            tokenraw = self.accessToken + self.appSecret
            self.apiToken = hashlib.sha256(tokenraw.encode('utf-8')).hexdigest()

        ParseRes = urlparse(self.instanceAddress)
        if ParseRes.scheme == '':
            ParseRes = urlparse("https://{}".format(self.instanceAddress))
        self.PRscheme = ParseRes.scheme
        self.instanceAddressUrl = "{0}://{1}".format(self.PRscheme, ParseRes.netloc)
        self.instanceAddressApiUrl = self.instanceAddressUrl + "/api"

        self.res = requests.post(self.instanceAddressApiUrl + "/meta")

        if self.res.status_code != 200:
            raise MisskeyInitException("API Meta check failed: Server returned HTTP {}\nHave you entered an address that is not a Misskey instance?".format(self.res.status_code))

        self.metaDic = json.loads(self.res.text)

        if self.apiToken != None:
            self.credentials = self.i()
            if 'isAdmin' in self.credentials:
                self.i_isAdmin = self.credentials['isAdmin']

    def hash_apitoken(self, accessToken, appSecret, substitution=False):
        """
        HASH APITOKEN
        """
        tokenraw = self.accessToken + self.appSecret
        apiToken = hashlib.sha256(tokenraw.encode('utf-8')).hexdigest()

        if substitution == True:
            self.apiToken = apiToken

        return apiToken

    def meta(self,useCache=False):
        """
        READ INSTANCE META INFORMATION
        """
        if useCache == True and self.metaDic != None:
            return self.metaDic

        self.res = requests.post(self.instanceAddressApiUrl + "/meta")
        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        self.metaDic = json.loads(self.res.text)
        return json.loads(self.res.text)

    def stats(self):
        """
        READ INSTANCE STATS
        """

        self.res = requests.post(self.instanceAddressApiUrl + "/stats")

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

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
                    'account/read',
                    'account/write',
                    'messaging-read',
                    'messaging-write',
                    'vote-read',
                    'vote-write'
                    ], callbackUrl=None):
        """
        CREATE APP FUNCTION

        Attribute:
        * : Required
        - appName * : Application's Name
        - description * : Application's Description
        - permission * : Application's Permission (See "Available Permissions" Section)
        - callbackUrl : Application's Callback URL

        Return:
        - Responce (type: dict)

        Avaliable Permissions:
        - account-read
        - account-write
        - note-read
        - note-write
        - reaction-read
        - reaction-write
        - following-read
        - following-write
        - drive-read
        - drive-write
        - notification-read
        - notification-write
        - favorite-read
        - favorites-read
        - favorite-write
        - account/read
        - account/write
        - messaging-read
        - messaging-write
        - vote-read
        - vote-write
        """
        headers = {'content-type': 'application/json'}

        ParseRes = urlparse(instanceAddress)
        if ParseRes.scheme == '':
            ParseRes = urlparse("https://{}".format(instanceAddress))
        PRscheme = ParseRes.scheme
        instanceAddressUrl = "{0}://{1}".format(PRscheme, ParseRes.netloc)
        instanceAddressApiUrl = instanceAddressUrl + "/api"

        if type(appName) != str:
            raise MisskeyArgumentException("name attribute must bt list type! but your name attribute is {}".format(type(name)))

        if type(description) != str:
            raise MisskeyArgumentException("description attribute must bt list type! but your description attribute is {}".format(type(description)))

        if type(permission) != list:
            raise MisskeyArgumentException("permission attribute must bt list type! but your permission attribute is {}".format(type(permission)))

        payload = {'name': appName, 'description': description, 'permission': permission, 'callbackUrl': callbackUrl}

        app = requests.post(instanceAddressApiUrl + "/app/create", data=json.dumps(payload), headers=headers)
        appjson = json.loads(app.text)

        if app.status_code != 200:
            if app.status_code == 400:
                raise MisskeyBadRequestException("Server returned HTTP 400: code: {0}, param: {1}, reason: {2}".format(appjson['error']['code'], appjson['error']['param'], appjson['error']['reason']))
            else:
                raise MisskeyResponseException("Server returned HTTP {}\nHave you entered an address that is not a Misskey instance?".format(app.status_code))

        return appjson

    @staticmethod
    def auth_session_generate(instanceAddress, appSecret):
        """
        AUTHORIZE APPLICATION

        Attribute:
        - instanceAddress * : Instance Address
        - appSecret * : Application Secret Key
        """
        headers = {'content-type': 'application/json'}

        ParseRes = urlparse(instanceAddress)
        if ParseRes.scheme == '':
            ParseRes = urlparse("https://{}".format(instanceAddress))
        PRscheme = ParseRes.scheme
        instanceAddressUrl = "{0}://{1}".format(PRscheme, ParseRes.netloc)
        instanceAddressApiUrl = instanceAddressUrl + "/api"

        payload = {'appSecret': appSecret}

        auth = requests.post(instanceAddressApiUrl + "/auth/session/generate", data=json.dumps(payload), headers=headers)
        authjson = json.loads(auth.text)

        if auth.status_code != 200:
            if auth.status_code == 400:
                raise MisskeyBadRequestException("Server returned HTTP 400: {}".format(authjson['error']))
            else:
                raise MisskeyResponseException("Server returned HTTP {}\nHave you entered an address that is not a Misskey instance?".format(auth.status_code))

        return authjson

    @staticmethod
    def auth_session_userkey(instanceAddress, appSecret, token):
        """
        CHECK AUTHORIZED TOKEN

        Attribute:
        - instanceAddress * : Instance Address
        - appSecret * : Application Secret Key
        - token * : authorize token

        Return:
        - authorizejson (type: dict)
        """
        headers = {'content-type': 'application/json'}
        ParseRes = urlparse(instanceAddress)
        if ParseRes.scheme == '':
            ParseRes = urlparse("https://{}".format(instanceAddress))
        PRscheme = ParseRes.scheme
        instanceAddressUrl = "{0}://{1}".format(PRscheme, ParseRes.netloc)
        instanceAddressApiUrl = instanceAddressUrl + "/api"

        payload = {'appSecret': appSecret, 'token': token}

        authorize = requests.post(instanceAddressApiUrl + "/auth/session/userkey", data=json.dumps(payload), headers=headers)
        authorizejson = json.loads(authorize.text)
        if authorize.status_code != 200:
            if authorize.status_code == 400:
                raise MisskeyBadRequestException("Server returned HTTP 400: {}".format(authorizejson['error']))
            else:
                raise MisskeyResponseException("Server returned HTTP {}\nHave you entered an address that is not a Misskey instance?".format(authorize.status_code))

        return authorizejson

    def i(self, useCache=False):
        """
        RETURNS YOUR CREDENTIAL

        Attribute:
        - useCache : use from class variable
        Return:
        - res (type: dict)
        """

        if useCache == True:
            return self.credentials

        self.res = requests.post(self.instanceAddressApiUrl + "/i", data=json.dumps({'i': self.apiToken}), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        self.credentials = json.loads(self.res.text)
        return json.loads(self.res.text)

    def notes_create(self, body=None, cw=None, visibility='public', visibleUserIds=None, viaMobile=False, geo=None, fileIds=None, replyId=None, renoteId=None, poll=None):
        """
        POST NOTE (WITH RENOTE QUOTE)

        Attribute:
        - body * : Note body
        - cw : Content Warning
        - visibility : visibility
        - viaMobile : Is it mark as Mobile
        """
        payload = {'i': self.apiToken, 'text': body, 'cw': cw, 'visibility': visibility, 'viaMobile': viaMobile, 'geo': geo}

        if visibleUserIds != None:
            payload['visibleUserIds'] = visibleUserIds

        if fileIds != None:
            payload['fileIds'] = fileIds

        if replyId != None and type(replyId) == str:
            payload['replyId'] = replyId

        if renoteId != None and type(renoteId) == str:
            payload['renoteId'] = renoteId

        if poll != None and type(poll) == list and len(poll) >= 2 and len(poll) <= 10:
            payload['poll'] = {"choices": poll}

        self.res = requests.post(self.instanceAddressApiUrl + "/notes/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'note-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def notes_renote(self, renoteId):
        """
        RENOTE FUNCTION

        Attribute:
        - renoteId : ID of will renote
        """
        payload = {'i': self.apiToken, 'renoteId': renoteId}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'note-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def notes_show(self, noteId):
        """
        POST SHOW

        Attribute:
        noteId * : Note ID
        """
        payload = {'i': self.apiToken, 'noteId': noteId}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/show", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def notes_delete(self, noteId):
        """
        POST SHOW

        Attribute:
        - noteId * : Note ID

        Return:
        - [boolean] (True: success)
        """
        payload = {'i': self.apiToken, 'noteId': noteId}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'note-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def notes_conversation(self, noteId, limit=None, offset=None):
        """
        POST SHOWS NOTES CONVERSATION

        Attribute:
        - noteId * : Note ID
        - limit : recieve limit
        - offset : pagenation
        """
        payload = {'noteId': noteId}

        if limit != None:
            payload['limit'] = int(limit)

        if offset != None:
            payload['offset'] = int(offset)

        self.res = requests.post(self.instanceAddressApiUrl + "/notes/conversation", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def notes_reactions(self, noteId, limit=None, offset=None):
        """
        POST SHOW REACTIONS

        Attribute:
        - noteId * : Note ID
        - limit : recieve limit
        - offset : pagenation
        """
        payload = {'noteId': noteId}

        if limit != None:
            payload['limit'] = int(limit)

        if offset != None:
            payload['offset'] = int(offset)

        self.res = requests.post(self.instanceAddressApiUrl + "/notes/reactions", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def notes_reactions_create(self, noteId, reaction='pudding'):
        """
        CREATE REACTION

        Attribute:
        - noteId * : Note ID
        - reaction : to send reaction
        """
        payload = {'i': self.apiToken, 'noteId': noteId, 'reaction': reaction}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/reactions/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'reaction-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def notes_reactions_delete(self, noteId):
        """
        CREATE REACTION

        Attribute:
        - noteId * : Note ID
        - reaction : to send reaction
        """
        payload = {'i': self.apiToken, 'noteId': noteId}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/reactions/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'reaction-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def notes_polls_recommendation(self, limit=None, offset=None):
        """
        RECOMMENDATION WITHIN POLL NOTES
        """
        payload = {'i': self.apiToken}

        if limit != None:
            payload['limit'] = limit

        if offset != None:
            payload['offset'] = offset

        self.res = requests.post(self.instanceAddressApiUrl + "/notes/polls/vote", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'vote-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def notes_polls_vote(self, noteId, choice):
        """
        VOTE TO NOTE INCLUDES POLLS
        """
        payload = {'i': self.apiToken, 'noteId': noteId, 'choice': choice}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/polls/vote", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'vote-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def local_timeline(self, withFiles=False, fileType=None, excludeNsfw=False, limit=None, offset=None, sinceId=None, untilId=None, sinceDate=None, untilDate=None):
        """
        READ TIMELINE OF LOCAL

        Attribute:
        - withFiles : show only include files
        - fileType : fileType dict
        - excludeNsfw : Don't show if it has NSFW flag
        - limit : receive limit
        - offset : pagination
        - sinceId : Since Note Id
        - untilId : Until Note Id
        - sinceDate : Since Date
        - untilDate : Until Date
        """
        payload = {'i': self.apiToken, 'excluceNsfw': excludeNsfw, 'withFiles': withFiles}

        if fileType != None:
            payload['fileType'] = fileType

        if limit != None:
            payload['limit'] = int(limit)

        if offset != None:
            payload['offset'] = int(offset)

        if sinceId != None:
            payload['sinceId'] = str(sinceId)

        if untilId != None:
            payload['untilId'] = str(untilId)

        if sinceDate != None:
            payload['sinceDate'] = int(sinceDate)

        if untilDate != None:
            payload['untilDate'] = int(untilDate)


        self.res = requests.post(self.instanceAddressApiUrl + "/notes/local-timeline", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def global_timeline(self, withFiles=False, fileType=None, excludeNsfw=False, limit=None, offset=None, sinceId=None, untilId=None, sinceDate=None, untilDate=None):
        """
        READ TIMELINE OF GLOBAL

        Attribute:
        - withFiles : show only include files
        - fileType : fileType dict
        - excludeNsfw : Don't show if it has NSFW flag
        - limit : receive limit
        - offset : pagination
        - sinceId : Since Note Id
        - untilId : Until Note Id
        - sinceDate : Since Date
        - untilDate : Until Date
        """
        payload = {'i': self.apiToken, 'excludeNsfw': excludeNsfw, 'withFiles': withFiles}

        if fileType != None:
            payload['fileType'] = fileType

        if limit != None:
            payload['limit'] = int(limit)

        if offset != None:
            payload['offset'] = int(offset)

        if sinceId != None:
            payload['sinceId'] = str(sinceId)

        if untilId != None:
            payload['untilId'] = str(untilId)

        if sinceDate != None:
            payload['sinceDate'] = int(sinceDate)

        if untilDate != None:
            payload['untilDate'] = int(untilDate)


        self.res = requests.post(self.instanceAddressApiUrl + "/notes/global-timeline", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def hybrid_timeline(self, withFiles=False, fileType=None, excludeNsfw=False, limit=None, offset=None, sinceId=None, untilId=None, sinceDate=None, untilDate=None, includeMyRenotes=True, includeRenotedMyNotes=True, includeLocalRenotes=True):
        """
        READ TIMELINE OF HYBRID(SOCIAL)

        Attribute:
        - withFiles : show only include files
        - fileType : fileType dict
        - excludeNsfw : Don't show if it has NSFW flag
        - limit : receive limit
        - offset : pagination
        - sinceId : Since Note Id
        - untilId : Until Note Id
        - sinceDate : Since Date
        - untilDate : Until Date
        - includeMyRenotes : include My Notes
        - includeRenotedMyNotes : include renoted my notes
        - includeLocalRenotes: include local renotes
        """
        payload = {'i': self.apiToken, 'withFiles': withFiles, 'excludeNsfw': excludeNsfw, 'includeMyRenotes': includeMyRenotes, 'includeRenotedMyNotes': includeMyRenotes, 'includeLocalRenotes': includeLocalRenotes}

        if fileType != None:
            payload['fileType'] = fileType

        if limit != None:
            payload['limit'] = int(limit)

        if offset != None:
            payload['offset'] = int(offset)

        if sinceId != None:
            payload['sinceId'] = str(sinceId)

        if untilId != None:
            payload['untilId'] = str(untilId)

        if sinceDate != None:
            payload['sinceDate'] = int(sinceDate)

        if untilDate != None:
            payload['untilDate'] = int(untilDate)


        self.res = requests.post(self.instanceAddressApiUrl + "/notes/hybrid-timeline", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def timeline(self, withFiles=False, fileType=None, excludeNsfw=False, limit=None, offset=None, sinceId=None, untilId=None, sinceDate=None, untilDate=None, includeMyRenotes=True, includeRenotedMyNotes=True, includeLocalRenotes=True):
        """
        READ TIMELINE OF HOME

        Attribute:
        - withFiles : show only include files
        - fileType : fileType dict
        - excludeNsfw : Don't show if it has NSFW flag
        - limit : receive limit
        - offset : pagination
        - sinceId : Since Note Id
        - untilId : Until Note Id
        - sinceDate : Since Date
        - untilDate : Until Date
        - includeMyRenotes : include My Notes
        - includeRenotedMyNotes : include renoted my notes
        - includeLocalRenotes: include local renotes
        """
        payload = {'i': self.apiToken, 'withFiles': withFiles, 'excludeNsfw': excludeNsfw, 'includeMyRenotes': includeMyRenotes, 'includeRenotedMyNotes': includeMyRenotes, 'includeLocalRenotes': includeLocalRenotes}

        if fileType != None:
            payload['fileType'] = fileType

        if limit != None:
            payload['limit'] = int(limit)

        if offset != None:
            payload['offset'] = int(offset)

        if sinceId != None:
            payload['sinceId'] = str(sinceId)

        if untilId != None:
            payload['untilId'] = str(untilId)

        if sinceDate != None:
            payload['sinceDate'] = int(sinceDate)

        if untilDate != None:
            payload['untilDate'] = int(untilDate)


        self.res = requests.post(self.instanceAddressApiUrl + "/notes/timeline", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def users_show(self, userId=None, userIds=None, username=None, host=None):
        """
        SHOW USER(S)
        """
        payload = {}

        if userId != None:
            payload['userId'] = userId

        if userIds != None:
            payload['userIds'] = userIds

        if username != None:
            payload['username'] = username

        if host != None:
            payload['host'] = host

        self.res = requests.post(self.instanceAddressApiUrl + "/users/show", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def following_create(self, userId):
        """
        FOLLOW USER
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/following/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'following-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def following_delete(self, userId):
        """
        UNFOLLOW USER
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/following/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'following-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def mute_list(self, limit=None, sinceId=None, untilId=None):
        """
        BLOCK LIST
        """
        payload = {'i': self.apiToken}

        if limit != None:
            payload['limit'] = limit

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['untilId'] = untilId

        self.res = requests.post(self.instanceAddressApiUrl + "/mute/list", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'account/read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def mute_create(self, userId):
        """
        MUTE USER
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/mute/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'account/write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def mute_delete(self, userId):
        """
        UNMUTE USER
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/mute/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'account/write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def blocking_list(self, limit=None, sinceId=None, untilId=None):
        """
        BLOCK LIST
        """
        payload = {'i': self.apiToken}

        if limit != None:
            payload['limit'] = limit

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['untilId'] = untilId

        self.res = requests.post(self.instanceAddressApiUrl + "/blocking/list", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'following-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def blocking_create(self, userId):
        """
        BLOCK USER
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/blocking/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'following-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def blocking_delete(self, userId):
        """
        UNBLOCK USER
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/blocking/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'following-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive(self):
        """
        SHOW DRIVE STATUS
        """
        payload = {'i': self.apiToken}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files(self, limit=None, sinceId=None, untilId=None, folderId=None, type=None):
        """
        SHOW DRIVE FILES
        """
        payload = {'i': self.apiToken, 'folderId': folderId}

        if limit != None:
            payload['limit'] = limit

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['untilId'] = untilId

        if type != None:
            payload['type'] = type

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files_create(self, filePath, folderId=None, isSensitive=False, force=False):
        """
        UPLOAD FILE
        """
        fileName = os.path.basename(filePath)
        fileAbs = os.path.abspath(filePath)
        fileBin = open(fileAbs, 'rb')
        fileMime = mimetypes.guess_type(filePath)
        filePayload = {'file': (fileName, fileBin, fileMime[0])}

        payload = {'i': self.apiToken, 'folderId': folderId, 'isSensitive': isSensitive, 'force': force}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files/create", data=payload, files=filePayload)
        fileBin.close()

        if self.res.status_code != 200:
            try:
                if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                    raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            except json.decoder.JSONDecodeError:
                pass
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files_upload_from_url(self, url, folderId=None, isSensitive=False, force=False):
        """
        UPLOAD FILE FROM URL
        """
        payload = {'i': self.apiToken, 'url': url, 'folderId': folderId, 'isSensitive': isSensitive, 'force': force}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files/upload_from_url", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files_show(self, fileId):
        """
        SHOW DRIVE FILE
        """
        payload = {'i': self.apiToken, 'fileId': fileId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files/show", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files_find(self, name, folderId=None):
        """
        FIND DRIVE FILES
        """
        payload = {'i': self.apiToken, 'name': name, 'folderId': folderId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files/find", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files_update(self, fileId, folderId='', name=None, isSensitive=None):
        """
        UPDATE DRIVE FILE
        """
        payload = {'i': self.apiToken, 'fileId': fileId}

        if folderId != '':
            if folderId == None:
                payload['folderId'] = None
            else:
                payload['folderId'] = folderId

        if isSensitive != None:
            payload['isSensitive'] = isSensitive

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files/update", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_files_delete(self, fileId):
        """
        DELETE DRIVE FILE
        """
        payload = {'i': self.apiToken, 'name': name, 'fileId': fileId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/files/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def drive_folders(self, limit=None, sinceId=None, untilId=None, folderId=None):
        """
        SHOW DRIVE FOLDERS
        """
        payload = {'i': self.apiToken, 'folderId': folderId}

        if limit != None:
            payload['limit'] = limit

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['untilId'] = untilId

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/folders",data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_folders_find(self, name, parentId=None):
        """
        FIND DRIVE FOLDERS
        """
        payload = {'i': self.apiToken, 'name': name, 'parentId': parentId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/folders/find", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_folders_create(self, name, parentId=None):
        """
        CREATE DRIVE FOLDER
        """
        payload = {'i': self.apiToken, 'name': name, 'parentId': parentId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/folders/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_folders_show(self, folderId):
        """
        SHOW DRIVE FOLDER
        """
        payload = {'i': self.apiToken, 'folderId': folderId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/folders/show", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_folders_update(self, folderId, name=None, parentId=''):
        """
        UPDATE DRIVE FOLDER
        """
        payload = {'i': self.apiToken, 'folderId': folderId}

        if name != None:
            payload['name'] = name

        if parentId != '':
            if parentId == None:
                payload['parentId'] = None
            else:
                payload['parentId'] = folderId

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/folders/update", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def drive_folders_delete(self, folderId):
        """
        DELETE DRIVE FOLDER
        """
        payload = {'i': self.apiToken, 'folderId': folderId}

        self.res = requests.post(self.instanceAddressApiUrl + "/drive/folders/delete", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'drive-write'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def games_reversi_games(self, limit=None, sinceId=None, untilId=None, my=False):
        """
        SHOW REVERSI GAMES
        """
        payload = {}

        if limit != None:
            payload['limit'] = limit

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['untildId'] = untildId

        if my == True:
            payload['i'] = self.apiToken
            payload['my'] = my

        self.res = requests.post(self.instanceAddressApiUrl + "/games/reversi/games", data=json.dumps(payload), headers=self.headers)

        if self.res.staus_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def games_reversi_games_show(self, gameId):
        """
        SHOW REVERSI GAME
        """
        payload = {'gameId': gameId}

        self.res = requests.post(self.instanceAddressApiUrl + "/games/reversi/games/show", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def games_reversi_games_surrender(self, gameId):
        """
        SURRENDER TO MATCHING REVERSI GAME
        """
        payload = {'i': self.apiToken, 'gameId': gameId}

        self.res = requests.post(self.instanceAddressApiUrl + "/games/reversi/games/surrender", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    @construction
    def games_reversi_match(self, userId):
        """
        REVERSI MATCH REQUEST
        """
        payload = {'i': self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/games/reversi/match", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code !=204:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def messaging_messages(self, userId, limit=None, sinceId=None, untilId=None, markAsRead=None):
        """
        SHOW MESSAGES
        """
        payload = {'i': self.apiToken, 'userId': userId}

        if limit != None:
            payload['limit'] = limit

        if sinceId != None:
            payload['sinceId'] = sinceId

        if untilId != None:
            payload['limit'] = untilId

        if markAsRead != None:
            payload['limit'] = markAsRead

        self.res = requests.post(self.instanceAddressApiUrl + "/messaging/messages", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'messaging-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def messaging_messages_create(self, userId, text=None, fileId=None):
        """
        SHOW MESSAGES HISTORY
        """
        payload = {'i': self.apiToken, 'userId': userId}

        if text != None:
            payload['text'] = text

        if fileId != None:
            payload['fileId'] = fileId

        self.res = requests.post(self.instanceAddressApiUrl + "/messaging/messages/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'messaging-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def messaging_history(self, limit=None):
        """
        SHOW MESSAGES HISTORY
        """
        payload = {'i': self.apiToken}

        if limit != None:
            payload['limit'] = limit

        self.res = requests.post(self.instanceAddressApiUrl + "/messaging/history", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'messaging-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def messaging_messages_read(self, messageId):
        """
        MESSAGE MARK AS READ
        """
        payload = {'i': self.apiToken, 'messageId': messageId}

        self.res = requests.post(self.instanceAddressApiUrl + "/messaging/messages/read", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            if 'error' in json.loads(self.res.text) and json.loads(self.res.text)['error'] == 'PERMISSION_DENIED':
                raise MisskeyPermissionException("Permission denied! this function needs permission 'messaging-read'!")
            else:
                raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    ##### ADMINISTRATOR FUNCTIONS
    def admin_invite(self):
        """
        CREATE INVITE CODE
        """
        isAdmin(self.i_isAdmin)
        payload = {"i": self.apiToken}

        self.res = requests.post(self.instanceAddressApiUrl + "/admin/invite", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)

    def admin_verify(self, userId):
        """
        MARK AS VERIFY
        """
        isAdmin(self.i_isAdmin)
        payload = {"i": self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/admin/verify-user", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def admin_unverify(self, userId):
        """
        UNMARK AS VERIFY
        """
        isAdmin(self.i_isAdmin)
        payload = {"i": self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/admin/unverify-user", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def admin_moderators_add(self, userId):
        """
        MARK AS MODERATOR
        """
        isAdmin(self.i_isAdmin)
        payload = {"i": self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/admin/moderators/add", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    def admin_moderators_remove(self, userId):
        """
        UNMARK AS MODERATOR
        """
        isAdmin(self.i_isAdmin)
        payload = {"i": self.apiToken, 'userId': userId}

        self.res = requests.post(self.instanceAddressApiUrl + "/admin/moderators/remove", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 204:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return True

    ### CUSTOM API
    def CUSTOM_API(self, api, payload=None, includeCred=False):
        """
        CUSTOM MISSKEY API
        """

        if includeCred == True:
            payload['i'] = self.apiToken

        self.res = requests.post(self.instanceAddressApiUrl + "/" + api, data=json.dumps(payload), headers=self.headers)

        if self.res.status_code == 204:
            return True
        elif self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))

        return json.loads(self.res.text)
