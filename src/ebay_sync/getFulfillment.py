#!/usr/bin/env python3

from .lib.api_request import APIrequest
from .lib.fulfillment import Fulfillment

class getFulfillment():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def setUri(self, uri):
        self.uri = uri
        return self

    def fetch(self):
        oauth_token = self.credentials.getOauthToken()
        access_token = APIrequest.getAccessToken(self.scope, self.credentials.ebay_refresh_token, oauth_token)
        self.content = APIrequest.getRESTContent(self.uri, access_token)
        return self

    def parse(self):
        m_fulfillment = Fulfillment(self.db)

        if self.content is None:
            tracking = self.uri.rsplit('/', 1)[1]

            m_fulfillment.setFulfillmentId(tracking)
            m_fulfillment.setTrackingId(tracking)
            m_fulfillment.add()
        else:
            m_fulfillment.setFulfillmentId(self.content['fulfillmentId'])
            m_fulfillment.setCarrier(self.content['shippingCarrierCode'])
            m_fulfillment.setTrackingId(self.content['shipmentTrackingNumber'])
            m_fulfillment.setFulfillmentDate(self.content['shippedDate'])
            m_fulfillment.add()

            m_fulfillment.setLineItemIds(self.content['lineItems'])
            m_fulfillment.addLineItems()
