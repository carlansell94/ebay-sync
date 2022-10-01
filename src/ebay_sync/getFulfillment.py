#!/usr/bin/env python3

from .lib.api_request import APIrequest
from .lib.fulfillment import Fulfillment

class getFulfillment():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials
        self.content = None
        self.uri = None

    def set_uri(self, uri):
        self.uri = uri
        return self

    def fetch(self):
        access_token = APIrequest.get_access_token(
            self.scope,
            self.credentials.ebay_refresh_token,
            self.credentials.get_oauth_token()
        )

        if access_token:
            self.content = APIrequest.get_rest_content(self.uri, access_token)
            return self
        else:
            return None

    def parse(self):
        m_fulfillment = Fulfillment(self.db)

        if self.content:
            id = self.content['shipmentTrackingNumber']
        else:
            id = self.uri.rsplit('/', 1)[1]
        
        m_fulfillment.set_tracking_id(id)

        if not m_fulfillment.already_exists():
            if self.content:
                m_fulfillment.set_fulfillment_id(self.content['fulfillmentId'])
                m_fulfillment.set_carrier(self.content['shippingCarrierCode'])
                m_fulfillment.set_fulfillment_date(self.content['shippedDate'])
                m_fulfillment.add()

                m_fulfillment.set_line_item_ids(self.content['lineItems'])
                m_fulfillment.add_line_items()
            else:
                m_fulfillment.set_fulfillment_id(id)
                m_fulfillment.add()
