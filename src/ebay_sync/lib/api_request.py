#!/usr/bin/env python3

from json import loads
from urllib import error, parse
from urllib.request import Request, urlopen
import time

class APIrequest:
    @staticmethod
    def _get_token(body: str, oauth_token: str, token_type: str):
        req = Request('https://api.ebay.com/identity/v1/oauth2/token',
                        data=body)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Authorization', 'Basic ' + oauth_token)

        try:
            with urlopen(req) as content:
                token = loads(content.read())[token_type]
                return token
        except error.HTTPError as e:
            body = loads(e.read().decode())
            print(f"[ERROR] {body['error']}: {body['error_description']}")
            return None

    @staticmethod
    def get_refresh_token(auth_code: str, oauth_token: str, runame: str):
        body = parse.urlencode({
            'grant_type': 'authorization_code',
            'redirect_uri': runame,
            'code': auth_code
        }).encode()

        return APIrequest._get_token(body, oauth_token, 'refresh_token')

    @staticmethod
    def get_access_token(scope: str, refresh_token: str, oauth_token: str) -> str:
        body = parse.urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': scope
        }).encode()

        return APIrequest._get_token(body, oauth_token, 'access_token')

    @staticmethod
    def get_rest_content(
        endpoint: str,
        access_token: str,
        headers: str=None,
        body: str=None
    ) -> str:
        req = Request(endpoint, headers=headers or {}, data=body)
        req.add_header('Authorization', 'Bearer ' + access_token)

        try:
            with urlopen(req) as content:
                json = loads(content.read())
                return json
        except error.HTTPError as e:
            return None

    @staticmethod
    def get_digital_signature_headers(
        endpoint: str,
        ebay_signing_key_jwe: str,
        get_signature: callable
    ) -> str:
        signature_params = (
            '("x-ebay-signature-key" "@method" "@path" "@authority");'
            f"created={int(time.time())}"
        )
        signature = get_signature(endpoint, signature_params)

        return {
            "Signature-Input": f"sig1={signature_params}",
            "Signature": f"sig1=:{signature}:",
            "x-ebay-signature-key": ebay_signing_key_jwe,
            "x-ebay-enforce-signature": "true",
        }

    @staticmethod
    def get_xml_content(call: str, credentials: dict, args: str) -> str:
        compat_level = 1119
        site_id = 3

        request = ('$xml_request = \'<?xml version="1.0" encoding="utf-8"?><'
                    + call
                    + 'Request xmlns="urn:ebay:apis:eBLBaseComponents">'
                    + '<RequesterCredentials><eBayAuthToken>'
                    + credentials.ebay_authnauth
                    + '</eBayAuthToken></RequesterCredentials>'
                    + args
                    + '</'
                    + call
                    + 'Request>')

        req = Request('https://api.ebay.com/ws/api.dll', request.encode())
        req.add_header('X-EBAY-API-COMPATIBILITY-LEVEL', compat_level)
        req.add_header('X-EBAY-API-DEV-NAME', credentials.ebay_dev_id)
        req.add_header('X-EBAY-API-APP-NAME', credentials.ebay_app_id)
        req.add_header('X-EBAY-API-CERT-NAME', credentials.ebay_cert_id)
        req.add_header('X-EBAY-API-CALL-NAME', call)
        req.add_header('X-EBAY-API-SITEID', site_id)
        req.add_header('Content-Type', "text/xml")

        with urlopen(req) as content:
            return content.read()

    @staticmethod
    def get_signing_key(access_token: str) -> dict:
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
        }

        req = Request(
            'https://apiz.ebay.com/developer/key_management/v1/signing_key',
            headers=headers,
            data='{"signingKeyCipher": "ED25519"}'.encode()
        )

        try:
            with urlopen(req) as content:
                return loads(content.read())
        except error.HTTPError as e:
            return None
