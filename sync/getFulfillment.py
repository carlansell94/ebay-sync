#!/usr/bin/env python3

from core.ebayapi import ebayAPI

class getFulfillment():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, credentials):
        self.credentials = credentials

    def setUri(self, uri):
        self.uri = uri
        return self

    def fetch(self):
        oauth_token = self.credentials.getOauthToken()
        access_token = ebayAPI.getAccessToken(self.scope, self.credentials.ebay_refresh_token, oauth_token)
        content = ebayAPI.getRESTContent(self.uri, access_token)
        return content
