#!/usr/bin/env python3

from urllib.request import Request, urlopen
from urllib import parse, error
import urllib
from os.path import dirname, abspath
from configparser import ConfigParser
from base64 import b64encode
import json

class Credentials:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(dirname(abspath(__file__)) + '/credentials.ini')

        self.db_name = self.config.get('db', 'name')[1:-1]
        self.db_user = self.config.get('db', 'user')[1:-1]
        self.db_password = self.config.get('db', 'password')[1:-1]
        self.refresh_token = self.config.get('ebay', 'refresh_token')[1:-1]
        self.app_id = self.config.get('ebay', 'app_id')[1:-1]
        self.dev_id = self.config.get('ebay', 'dev_id')[1:-1]
        self.cert_id = self.config.get('ebay', 'cert_id')[1:-1]
        self.authnauth = self.config.get('ebay', 'authnauth')[1:-1]

    def getOauthCredentials(self):
        return b64encode((self.app_id + ":" + self.cert_id).encode('ascii')).decode()

    def getAccessToken(self, scope):
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'scope': scope
        }

        data = parse.urlencode(body).encode()

        req = Request('https://api.ebay.com/identity/v1/oauth2/token', data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Authorization', 'Basic ' + self.getOauthCredentials())
        try:
            content = urlopen(req).read()
            token = json.loads(content)['access_token']
            return token
        except urllib.error.HTTPError as e:
            body = e.read().decode()
        
