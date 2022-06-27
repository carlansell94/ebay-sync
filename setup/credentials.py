#!/usr/bin/env python3

from base64 import b64encode
from configparser import ConfigParser
from os.path import dirname, abspath

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

    def setConfig(self, config: dict) -> None:
        for section, entry in config.items():
            for option, value in entry.items():
                self.parser[section] = entry
                setattr(self, section + '_' + option, value)

    def saveConfigFile(self):
        with open(self.filepath, 'w') as configFile:
            self.parser.write(configFile)

    def getOauthToken(self, app_id=None, cert_id=None):
        if app_id:
            enc_string = f"{app_id}:{cert_id}"
        else:
            enc_string = f"{self.ebay_app_id}:{self.ebay_cert_id}"

        return b64encode(enc_string.encode('ascii')).decode()
