#!/usr/bin/env python3

from .lib.api_request import APIrequest
from .lib.fulfillment import Fulfillment

class GetFulfillment():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials
        self.content = None
        self.uri = None

    def fetch(self, order_id):
        uri = ("https://api.ebay.com/sell/fulfillment/v1/order/"
               f"{order_id}/shipping_fulfillment")

        if access_token := APIrequest.get_access_token(
            self.scope,
            self.credentials.ebay_refresh_token,
            self.credentials.get_oauth_token()
        ):
            if content := APIrequest.get_rest_content(uri, access_token):
                self.content = content
                return self

        return None

    def parse(self):
        m_fulfillment = Fulfillment(self.db)

        for fulfillment in self.content.get('fulfillments'):
            m_fulfillment.set_fulfillment_id(fulfillment.get('fulfillmentId'))

            if not m_fulfillment.already_exists():
                m_fulfillment.set_tracking_id(fulfillment.get('shipmentTrackingNumber'))
                m_fulfillment.set_carrier(fulfillment.get('shippingCarrierCode'))
                m_fulfillment.set_fulfillment_date(fulfillment.get('shippedDate'))
                m_fulfillment.add()

            for line_item in fulfillment.get('lineItems'):
                m_fulfillment.set_line_item_id(line_item.get('lineItemId'))

                if not m_fulfillment.line_item_already_exists():
                    m_fulfillment.add_line_item()
