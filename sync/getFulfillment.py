#!/usr/bin/env python3

from urllib.request import Request, urlopen
from urllib import error
import json

class getFulfillment():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, credentials):
        self.credentials = credentials

    def setUri(self, uri):
        self.uri = uri
        return self

    def fetch(self):
        req = Request(self.uri)
        req.add_header('Authorization', 'Bearer '
                        + self.credentials.getAccessToken(self.scope))
        
        try:
            content = urlopen(req).read()
            response = json.loads(content)
            return response
        except error.HTTPError as e:
            body = e.read().decode()
