#!/usr/bin/env python3

from .lib.address import Address
from .lib.api_request import APIrequest
from .lib.line import Line
from .lib.payment import Payment
from .lib.refund import Refund
from .lib.sale import Sale

class GetSales:
    endpoint = 'https://api.ebay.com/sell/fulfillment/v1/order'
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials
        self.sales = None

    def fetch(self):
        if access_token := APIrequest.get_access_token(
            self.scope,
            self.credentials.ebay_refresh_token,
            self.credentials.get_oauth_token()
        ):
            self.sales = APIrequest.get_rest_content(
                self.endpoint,
                access_token
            )
            return self

        return None

    def sync_needed(self, order_id, api_last_updated) -> bool:
        if db_last_updated := Sale.get_last_updated(self.db, order_id):
            if (db_last_updated[0].strftime("%Y-%m-%dT%H:%M:%S.000Z")
                == api_last_updated):
                return False

        return True

    def parse(self) -> None:
        for order in self.sales.get('orders'):
            order_id = order.get('orderId')

            if self.sync_needed(order_id, order.get('lastModifiedDate')):
                if not self.parse_order(order):
                    continue

                # API returns one address per fulfillmentStartInstructions array
                self.parse_address(
                    order_id,
                    order.get('fulfillmentStartInstructions')[0].get('shippingStep').get('shipTo')
                )

                for line_item in order.get('lineItems'):
                    self.parse_line_item(order_id, line_item)

    def parse_order(self, order) -> bool:
        m_order = Sale(db=self.db)
        m_order.order_id = order.get('orderId')
        m_order.legacy_order_id = order.get('legacyOrderId')
        m_order.sale_date = order.get('creationDate')
        m_order.buyer_username = order.get('buyer').get('username')
        m_order.payment_status = order.get('orderPaymentStatus')
        m_order.fulfillment_status = order.get('orderFulfillmentStatus')
        m_order.fee = order.get('totalMarketplaceFee').get('value')
        m_order.last_updated = order.get('lastModifiedDate')

        if not m_order.valid:
            return False

        if m_order.exists():
            return m_order.update()

        return m_order.add()

    def parse_line_item(self, order_id, line_item) -> None:
        m_line_item = Line(db=self.db)
        m_line_item.order_id = order_id
        m_line_item.fulfillment_status = line_item.get('lineItemFulfillmentStatus')

        if m_line_item.exists():
            m_line_item.update()
        else:
            m_line_item.item_id = line_item.get('legacyItemId')
            m_line_item.line_item_id = line_item.get('lineItemId')
            m_line_item.title = line_item.get('title')
            m_line_item.sale_format = line_item.get('soldFormat')
            m_line_item.quantity = line_item.get('quantity')
            m_line_item.item_cost = line_item.get('lineItemCost').get('value')
            m_line_item.postage_cost = line_item.get('deliveryCost').get('shippingCost').get('value')
            m_line_item.currency = line_item.get('lineItemCost').get('currency')
            m_line_item.add()

    def parse_address(self, order_id, address) -> None:
        m_address = Address(db=self.db)
        m_address.order_id = order_id
        m_address.buyer_name = address.get('fullName')
        m_address.address_line_1 = address.get('contactAddress').get('addressLine1')
        m_address.address_line_2 = address.get('contactAddress').get('addressLine2')
        m_address.city = address.get('contactAddress').get('city')
        m_address.county = address.get('contactAddress').get('stateOrProvince')
        m_address.post_code = address.get('contactAddress').get('postalCode')
        m_address.country_code = address.get('contactAddress').get('countryCode')

        if not m_address.exists():
            m_address.address_id = m_address.add()

        if not m_address.order_exists():
            m_address.add_order()
