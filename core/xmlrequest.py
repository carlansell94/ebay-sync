#!/usr/bin/env python3

from urllib.request import Request, urlopen
from core.credentials import Credentials

class XMLRequest:
    def __init__(self):
        self.credentials = Credentials()
        self.compat_level = 1119
        self.site_id = 3

    def getRequest(self, call, args):
        request = ('$xml_request = \'<?xml version="1.0" encoding="utf-8"?><'
                    + call
                    + 'Request xmlns="urn:ebay:apis:eBLBaseComponents">'
                    + '<RequesterCredentials><eBayAuthToken>'
                    + self.credentials.authnauth
                    + '</eBayAuthToken></RequesterCredentials>'
                    + args
                    + '</'
                    + call
                    + 'Request>')

        req = Request('https://api.ebay.com/ws/api.dll', request.encode())
        req.add_header('X-EBAY-API-COMPATIBILITY-LEVEL', self.compat_level)
        req.add_header('X-EBAY-API-DEV-NAME', self.credentials.dev_id)
        req.add_header('X-EBAY-API-APP-NAME', self.credentials.app_id)
        req.add_header('X-EBAY-API-CERT-NAME', self.credentials.cert_id)
        req.add_header('X-EBAY-API-CALL-NAME', call)
        req.add_header('X-EBAY-API-SITEID', self.site_id)
        req.add_header('Content-Type', "text/xml")
        content = urlopen(req).read()
        return content