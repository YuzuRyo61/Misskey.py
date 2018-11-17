# -*- coding: utf-8 -*-

from Misskey.Exceptions import *

import requests
import json
import pprint
import hashlib

from urllib.parse import urlparse

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
        self.res = None

        if self.apiToken == None and self.appSecret != None and self.accessToken != None:
            tokenraw = self.accessToken + self.appSecret
            self.apiToken = hashlib.sha256(tokenraw.encode('utf-8')).hexdigest()

        ParseRes = urlparse(self.instanceAddress)
        if ParseRes.scheme == '':
            ParseRes = urlparse("https://{}".format(self.instanceAddress))
        self.PRscheme = ParseRes.scheme
        self.instanceAddressUrl = "{0}://{1}".format(self.PRscheme, ParseRes.netloc)
        self.instanceAddressApiUrl = self.instanceAddressUrl + "/api"

        meta = requests.post(self.instanceAddressApiUrl + "/meta")

        if meta.status_code != 200:
            raise MisskeyInitException("API Meta check failed: Server returned HTTP {}\nHave you entered an address that is not a Misskey instance?".format(meta.status_code))
        
        self.metaDic = json.loads(meta.text)

    def meta(self,useCache=False):
        """
        LOAD INSTANCE META INFORMATION
        """
        if useCache == True and self.metaDic != None:
            return self.metaDic
        
        self.res = requests.post(self.instanceAddressApiUrl + "/meta")
        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))
        
        return json.loads(self.res.text)

    @staticmethod
    def create_app(instanceAddress, appName, description, permission, callbackUrl=None):
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

    def i(self):
        """
        RETURNS YOUR CREDENTIAL

        Return:
        - res (type: dict)
        """
        self.res = requests.post(self.instanceAddressApiUrl + "/i", data=json.dumps({'i': self.apiToken}), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))
        
        return json.loads(self.res.text)

    def note_post(self, body, cw=None, visibility='public', viaMobile=False):
        """
        POST NOTE

        Attribute:
        - body * : Note body
        """
        payload = {'i': self.apiToken, 'text': body, 'visibility': visibility, 'viaMobile': viaMobile}
        self.res = requests.post(self.instanceAddressApiUrl + "/notes/create", data=json.dumps(payload), headers=self.headers)

        if self.res.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(self.res.status_code))
        
        return json.loads(self.res.text)