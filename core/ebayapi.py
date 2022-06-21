#!/usr/bin/env python3

from urllib.request import Request, urlopen
from urllib import error, parse
from json import loads

class ebayAPI:
    @staticmethod
    def getAccessToken(scope: str, refresh_token: str, oauth_token: str) -> str:
        body = parse.urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': scope
        }).encode()

        req = Request('https://api.ebay.com/identity/v1/oauth2/token',
                        data=body)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Authorization', 'Basic ' + oauth_token)

        try:
            content = urlopen(req).read()
            token = loads(content)['access_token']
            return token
        except error.HTTPError as e:
            body = e.read().decode()
    
    @staticmethod
    def getRESTContent(endpoint: str, access_token: str) -> str:
        req = Request(endpoint)
        req.add_header('Authorization', 'Bearer ' + access_token)

        try:
            content = urlopen(req).read()
            json = loads(content)
            return json
        except error.HTTPError as e:
            body = e.read().decode()
            print(body)

    @staticmethod
    def getXMLContent(call: str, credentials: dict, args: str) -> str:
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
        content = urlopen(req).read()
        return content
