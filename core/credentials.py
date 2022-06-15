#!/usr/bin/env python3

from urllib.request import Request, urlopen
from urllib import error, parse
from os.path import dirname, abspath
from configparser import ConfigParser
from base64 import b64encode
import json

class Credentials:
    def __init__(self) -> None:
        self.parser = ConfigParser()
        self.filepath = dirname(abspath(__file__)) + '/credentials.ini'

    def readConfigFile(self) -> bool:
        config = self.parser.read(self.filepath)

        if not config:
            return False
        else:
            for section in self.parser.sections():
                for option in self.parser.options(section):
                    value = self.parser.get(section, option)
                    setattr(self, section + '_' + option, value)

            return True

    def getOauthCredentials(self):
        return b64encode((self.ebay_app_id + ":" + self.ebay_cert_id).encode('ascii')).decode()

    def getAccessToken(self, scope: str) -> str:
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.ebay_refresh_token,
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
        except error.HTTPError as e:
            body = e.read().decode()
