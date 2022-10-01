#!/usr/bin/env python3

from base64 import b64encode
from configparser import ConfigParser
from pathlib import Path

class Credentials:
    def __init__(self) -> None:
        self.parser = ConfigParser()
        self.filepath = str(Path(__file__).parent.absolute()) + '/credentials.ini'

    def read_config_file(self) -> bool:
        config = self.parser.read(self.filepath)

        if not config:
            return False
        else:
            for section in self.parser.sections():
                for option in self.parser.options(section):
                    value = self.parser.get(section, option)
                    setattr(self, section + '_' + option, value)

            return True

    def set_config(self, config: dict) -> None:
        for section, entry in config.items():
            for option, value in entry.items():
                self.parser[section] = entry
                setattr(self, section + '_' + option, value)

    def save_config_file(self):
        with open(self.filepath, 'w') as config_file:
            self.parser.write(config_file)

    def get_oauth_token(self, app_id=None, cert_id=None):
        if app_id:
            enc_string = f"{app_id}:{cert_id}"
        else:
            enc_string = f"{self.ebay_app_id}:{self.ebay_cert_id}"

        return b64encode(enc_string.encode('ascii')).decode()

    def set_option_value(self, option: str, value: str) -> None:
        setattr(self, option, value)
        section, option = option.split("_", 1)
        self.parser.set(section, option, value)
