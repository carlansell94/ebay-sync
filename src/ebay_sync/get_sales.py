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
                order_items = []
                if not self.parse_order(order):
                    continue

                # API returns one address per fulfillmentStartInstructions array
                self.parse_address(
                    order_id,
                    order.get('fulfillmentStartInstructions')[0].get('shippingStep').get('shipTo')
                )

                for line_item in order.get('lineItems'):
                    item_payment_info = self.parse_line_item(order_id, line_item)
                    order_items.append(item_payment_info)

                for payment in order.get('paymentSummary').get('payments'):
                    payment_id = self.parse_payment(order, payment, order_items)

                for refund in order.get('paymentSummary').get('refunds'):
                    self.parse_refund(payment_id, refund)

    def parse_order(self, order) -> bool:
        m_order = Sale(db=self.db)
        m_order.order_id = order.get('orderId')
        m_order.legacy_order_id = order.get('legacyOrderId')
        m_order.sale_date = order.get('creationDate')
        m_order.buyer_username = order.get('buyer').get('username')
        m_order.status = order.get('orderFulfillmentStatus')
        m_order.fee = order.get('totalMarketplaceFee').get('value')
        m_order.last_updated = order.get('lastModifiedDate')

        if not m_order.valid:
            return False

        if m_order.exists():
            return m_order.update()

        return m_order.add()

    def parse_line_item(self, order_id, line_item) -> dict:
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
            m_line_item.add()

        payment_info = {
            'line_item_id': line_item.get('lineItemId'),
            'currency': line_item.get('lineItemCost').get('currency'),
            'cost': line_item.get('lineItemCost').get('value'),
            'postage_cost': line_item.get('deliveryCost').get('shippingCost').get('value')
        }

        return payment_info

    def parse_payment(self, order, payment, items) -> int:
        m_payment = Payment(db=self.db)

        m_payment.processor_payment_id = order.get('salesRecordReference')
        m_payment.processor_name = payment.get('paymentMethod')
        m_payment.status = order.get('orderPaymentStatus')

        if not m_payment.exists():
            m_payment.order_id = order.get('orderId')
            m_payment.transaction_date = payment.get('paymentDate')
            m_payment.update_date = payment.get('paymentDate')
            m_payment.transaction_amount = order.get('pricingSummary').get('total').get('value')
            m_payment.transaction_currency = order.get('pricingSummary').get('total').get('currency')
            m_payment.fee_currency = order.get('pricingSummary').get('total').get('currency')
            m_payment.add()
            m_payment.add_items(items)
        else:
            m_payment.update_items(items)

        return m_payment.payment_id

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

    def parse_refund(self, payment_id, refund) -> bool:
        m_refund = Refund(db=self.db)
        m_refund.processor_refund_id = refund.get('refundId')

        if not m_refund.exists():
            m_refund.date = refund.get('refundDate')
            m_refund.original_payment_id = payment_id
            m_refund.amount = refund.get('amount').get('value')
            m_refund.currency = refund.get('amount').get('currency')
            m_refund.fee_currency = refund.get('amount').get('currency')

            if not m_refund.valid:
                return False

            m_refund.add()

        return True
