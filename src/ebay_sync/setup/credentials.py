#!/usr/bin/env python3

from base64 import b64encode
from configparser import ConfigParser
from pathlib import Path
from urllib.parse import urlparse
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from ..lib.logger import Logger

class Credentials:
    def __init__(self) -> None:
        current_path = str(Path(__file__).parent.absolute())
        self.parser = ConfigParser()
        self.filepath = current_path + '/credentials.ini'
        self.private_key_filepath = current_path + '/digital_signature.key'
        self.ebay_app_id = None
        self.ebay_cert_id = None
        self.ebay_signing_key_jwe = None

    def _read_digital_signature_private_key(self):
        try:
            return Path(self.private_key_filepath).read_text(encoding="UTF-8")
        except FileNotFoundError as error:
            msg = (
                """Digital signature private key not found. Please run ebay_sync -k """
                """to generate a new signing key."""
            )
            Logger.create_entry(message=msg, entry_type="error")
            return False

    def save_digital_signature_private_key(self, key: str) -> bool:
        try:
            Path(self.private_key_filepath).write_text(
                f"""-----BEGIN PRIVATE KEY-----\n{key}\n-----END PRIVATE KEY-----""",
                encoding="UTF-8"
            )
            return True
        except (FileNotFoundError, IsADirectoryError, PermissionError) as error:
            msg = f"Unable to save digital signature private key: {error}"
            Logger.create_entry(message=msg, entry_type="error")
            return False

    def read_config_file(self) -> bool:
        if self.parser.read(self.filepath):
            for section in self.parser.sections():
                for option in self.parser.options(section):
                    value = self.parser.get(section, option)
                    setattr(self, section + '_' + option, value)

            return True

        return False

    def set_config(self, config: dict) -> None:
        for section, entry in config.items():
            for option, value in entry.items():
                self.parser[section] = entry
                setattr(self, section + '_' + option, value)

    def set_option_value(self, option: str, value: str) -> None:
        setattr(self, option, value)
        section, option = option.split("_", 1)
        self.parser.set(section, option, value)

    def save_config_file(self):
        with open(self.filepath, 'w', encoding="utf-8") as config_file:
            self.parser.write(config_file)

    def get_oauth_token(self, app_id=None, cert_id=None):
        if app_id:
            enc_string = f"{app_id}:{cert_id}"
        else:
            enc_string = f"{self.ebay_app_id}:{self.ebay_cert_id}"

        return b64encode(enc_string.encode('ascii')).decode()

    def get_content_digest(self, content: str) -> str:
        hasher = SHA256.new()
        hasher.update(bytes(content, encoding="utf-8"))
        return b64encode(hasher.digest()).decode()

    def get_digital_signature(
        self,
        request_url: str,
        signature_params: str,
        content_digest=False
    ) -> str:
        method = 'POST' if content_digest else 'GET'
        url = urlparse(request_url)
        params = (
            f'"x-ebay-signature-key": {self.ebay_signing_key_jwe}\n'
            f'"@method": {method}\n'
            f'"@path": {url.path}\n'
            f'"@authority": {url.netloc}\n'
            f'"@signature-params": {signature_params}'
        )

        if content_digest:
            params += f'\n"content-digest": {content_digest}'

        try:
            private_key = ECC.import_key(self._read_digital_signature_private_key())
            signer = eddsa.new(private_key, mode='rfc8032')
            return b64encode(signer.sign(params.encode())).decode()
        except ValueError as error:
            msg = f"Error creating digital signature: {error}"
            Logger.create_entry(message=msg, entry_type="error")
            return False
