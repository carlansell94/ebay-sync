#!/usr/bin/env python3

from .lib.address import Address
from .lib.api_request import APIrequest
from .lib.line import Line
from .lib.payment import Payment
from .lib.refund import Refund
from .lib.sale import Sale

class getSales:
    endpoint = 'https://api.ebay.com/sell/fulfillment/v1/order'
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials
        self.sales = None

    def fetch(self):
        access_token = APIrequest.get_access_token(
            self.scope,
            self.credentials.ebay_refresh_token,
            self.credentials.get_oauth_token()
        )

        if access_token:
            self.sales = APIrequest.get_rest_content(
                self.endpoint,
                access_token
            )
            return self
        else:
            return None

    def sync_needed(self, order_id, api_last_updated) -> bool:
        db_last_updated = Sale.get_last_updated(self.db, order_id)

        if db_last_updated != False:
            db_last_updated = db_last_updated[0][0].strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if api_last_updated == db_last_updated:
            return False

        return True

    def get_fulfillment_links(self):
        fulfillment_links = []

        for sale in self.sales['orders']:
            for fulfillment_link in sale['fulfillmentHrefs']:
                fulfillment_links.append(fulfillment_link)

        return fulfillment_links

    def parse(self) -> None:
        for order in self.sales['orders']:
            order_id = order['orderId'].split('!')[0]
            order_items = []

            if self.sync_needed(order_id, order['lastModifiedDate']):
                self.parse_order(order)

                for line_item in order['lineItems']:
                    item_payment_info = self.parse_line_item(order_id, line_item)
                    order_items.append(item_payment_info)

                for payment in order['paymentSummary']['payments']:
                    payment_id = self.parse_payment(order, payment, order_items)

                for address in order['fulfillmentStartInstructions']:
                    self.parse_address(order_id, address)

                for refund in order['paymentSummary']['refunds']:
                    self.parse_refund(payment_id, refund)

    def parse_order(self, order) -> None:
        m_order = Sale(self.db)
        m_order.set_order_id(order['orderId'].split('!')[0])
        m_order.set_legacy_order_id(order['legacyOrderId'])
        m_order.set_sale_date(order['creationDate'])
        m_order.set_buyer_username(order['buyer']['username'])
        m_order.set_status(order['orderFulfillmentStatus'])
        m_order.set_fee(order['totalMarketplaceFee']['value'])
        m_order.set_last_updated(order['lastModifiedDate'])
        m_order.add()

    def parse_line_item(self, order_id, line_item) -> dict:
        m_line_item = Line(self.db)
        m_line_item.set_order_id(order_id)
        m_line_item.set_item_id(line_item['legacyItemId'])
        m_line_item.set_line_item_id(line_item['lineItemId'])
        m_line_item.set_title(line_item['title'])
        m_line_item.set_sale_format(line_item['soldFormat'])
        m_line_item.set_quantity(line_item['quantity'])
        m_line_item.set_fulfillment_status(line_item['lineItemFulfillmentStatus'])
        m_line_item.add()

        payment_info = {
            'line_item_id': line_item['lineItemId'],
            'currency': line_item['lineItemCost']['currency'],
            'cost': line_item['lineItemCost']['value'],
            'postage_cost': line_item['deliveryCost']['shippingCost']['value']
        }

        return payment_info

    def parse_payment(self, order, payment, items) -> int:
        m_payment = Payment(self.db)

        m_payment.set_processor_id(order['salesRecordReference'])
        m_payment.set_processor_name(payment['paymentMethod'])
        m_payment.set_payment_status(order['orderPaymentStatus'])

        if not m_payment.already_exists():
            m_payment.set_order_id(order['orderId'].split('!')[0])
            m_payment.set_payment_date(payment['paymentDate'])
            m_payment.set_update_date(payment['paymentDate'])
            m_payment.set_payment_amount(order['pricingSummary']['total']['value'])
            m_payment.set_payment_currency(order['pricingSummary']['total']['currency'])
            m_payment.set_fee_amount(0)
            m_payment.set_fee_currency(order['pricingSummary']['total']['currency'])
            m_payment.add()

            payment_id = m_payment.get_payment_id()
            m_payment.add_items(items)
        else:
            payment_id = m_payment.get_payment_id()
            m_payment.update_items(items)

        return payment_id

    def parse_address(self, order_id, address) -> None:
        address = address['shippingStep']['shipTo']
        m_address = Address(self.db)
        m_address.set_order_id(order_id)
        m_address.set_buyer_name(address['fullName'])
        m_address.set_address_line_1(address['contactAddress']['addressLine1'])
        m_address.set_city(address['contactAddress']['city'])

        try:
            m_address.set_county(address['contactAddress']['stateOrProvince'])
        except KeyError:
            m_address.set_county("")

        m_address.set_post_code(address['contactAddress']['postalCode'])
        m_address.set_country_code(address['contactAddress']['countryCode'])

        if not m_address.already_exists():
            m_address.set_id(m_address.add())

        m_address.add_order()

    def parse_refund(self, payment_id, refund) -> None:
        m_refund = Refund(self.db)
        m_refund.set_id(refund['refundId'])
        m_refund.set_processor_name('EBAY')

        if not m_refund.already_exists():
            m_refund.set_date(refund['refundDate'])
            m_refund.set_original_payment_id(payment_id)
            m_refund.set_amount(refund['amount']['value'])
            m_refund.set_currency(refund['amount']['currency'])
            m_refund.set_fee(0)
            m_refund.set_fee_currency(refund['amount']['currency'])
            m_refund.add()
