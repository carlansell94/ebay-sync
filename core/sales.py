#!/usr/bin/env python3

from urllib.request import Request, urlopen
from urllib import parse
import json

class Sales():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, credentials):
        self.credentials = credentials

    def get(self):
        req = Request('https://api.ebay.com/sell/fulfillment/v1/order')
        req.add_header('Authorization', 'Bearer '
                        + self.credentials.getAccessToken(Sales.scope))
        content = urlopen(req).read()
        response = json.loads(content)
        return response
