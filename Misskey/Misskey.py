# -*- coding: utf-8 -*-

from Misskey.Exceptions import MisskeyInitException, MisskeyResponseException

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
        - apiToken : sha256 hashed from appSecret and accessToken (If If this is set, we will preferentially use this.)
        """
        self.instanceAddress = instanceAddress
        self.appSecret = appSecret
        self.accessToken = accessToken
        self.apiToken = apiToken
        self.metaDic = None

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
        if useCache == True and self.metaDic != None:
            return self.metaDic
        
        meta = requests.post(self.instanceAddressApiUrl + "/meta")
        if meta.status_code != 200:
            raise MisskeyResponseException("Server returned HTTP {}".format(meta.status_code))
        
        return json.loads(meta.text)

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
        pass