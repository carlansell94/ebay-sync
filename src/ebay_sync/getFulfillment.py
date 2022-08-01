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
        access_token = APIrequest.getAccessToken(
            self.scope,
            self.credentials.ebay_refresh_token,
            self.credentials.getOauthToken()
        )

        if access_token:
            self.content = APIrequest.getRESTContent(self.uri, access_token)
            return self
        else:
            return None

    def parse(self):
        m_fulfillment = Fulfillment(self.db)

        if self.content:
            id = self.content['shipmentTrackingNumber']
        else:
            id = self.uri.rsplit('/', 1)[1]
        
        m_fulfillment.setTrackingId(id)

        if not m_fulfillment.alreadyExists():
            if self.content:
                m_fulfillment.setFulfillmentId(self.content['fulfillmentId'])
                m_fulfillment.setCarrier(self.content['shippingCarrierCode'])
                m_fulfillment.setFulfillmentDate(self.content['shippedDate'])
                m_fulfillment.add()

                m_fulfillment.setLineItemIds(self.content['lineItems'])
                m_fulfillment.addLineItems()
            else:
                m_fulfillment.setTrackingId(id)
                m_fulfillment.add()
