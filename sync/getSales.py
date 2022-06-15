#!/usr/bin/env python3

from model.sale import Sale
from model.line import Line
from model.address import Address
from model.payment import Payment
from model.refund import Refund
from urllib.request import Request, urlopen
import json

class getSales:
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self):
        req = Request('https://api.ebay.com/sell/fulfillment/v1/order')
        req.add_header('Authorization', 'Bearer '
                        + self.credentials.getAccessToken(self.scope))
        content = urlopen(req).read()
        self.sales = json.loads(content)
        return self

    def syncNeeded(self, order_id, api_last_updated) -> bool:
        db_last_updated = Sale.getLastUpdated(self.db, order_id)

        if db_last_updated != False:
            db_last_updated = db_last_updated[0][0].strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if api_last_updated == db_last_updated:
            return False

        return True

    def getFulfillmentLinks(self):
        fulfillmentLinks = []

        for sale in self.sales['orders']:
            for fulfillment_link in sale['fulfillmentHrefs']:
                fulfillmentLinks.append(fulfillment_link)

        return fulfillmentLinks

    def parse(self) -> None:
        for order in self.sales['orders']:
            order_id = order['orderId'].split('!')[0]
            order_items = []

            if self.syncNeeded(order_id, order['lastModifiedDate']):
                self.parseOrder(order)

                for line_item in order['lineItems']:
                    item_payment_info = self.parseLineItem(order_id, line_item)
                    order_items.append(item_payment_info)

                for payment in order['paymentSummary']['payments']:
                    payment_id = self.parsePayment(order, payment, order_items)

                for address in order['fulfillmentStartInstructions']:
                    self.parseAddress(order_id, address)

                for refund in order['paymentSummary']['refunds']:
                    self.parseRefund(payment_id, refund)

    def parseOrder(self, order) -> None:
        m_order = Sale(self.db)
        m_order.setOrderId(order['orderId'].split('!')[0])
        m_order.setLegacyOrderId(order['legacyOrderId'])
        m_order.setSaleDate(order['creationDate'])
        m_order.setBuyerUsername(order['buyer']['username'])
        m_order.setStatus(order['orderFulfillmentStatus'])
        m_order.setFee(order['totalMarketplaceFee']['value'])
        m_order.setLastUpdated(order['lastModifiedDate'])
        m_order.add()

    def parseLineItem(self, order_id, line_item) -> dict:
        m_line_item = Line(self.db)
        m_line_item.setOrderId(order_id)
        m_line_item.setItemId(line_item['legacyItemId'])
        m_line_item.setLineItemId(line_item['lineItemId'])
        m_line_item.setTitle(line_item['title'])
        m_line_item.setSaleFormat(line_item['soldFormat'])
        m_line_item.setQuantity(line_item['quantity'])
        m_line_item.setFulfillmentStatus(line_item['lineItemFulfillmentStatus'])
        m_line_item.add()

        payment_info = {
            'line_item_id': line_item['lineItemId'],
            'currency': line_item['lineItemCost']['currency'],
            'cost': line_item['lineItemCost']['value'],
            'postage_cost': line_item['deliveryCost']['shippingCost']['value']
        }

        return payment_info

    def parsePayment(self, order, payment, items) -> int:
        m_payment = Payment(self.db)

        m_payment.setProcessorId(order['salesRecordReference'])
        m_payment.setProcessorName(payment['paymentMethod'])
        m_payment.setPaymentStatus(order['orderPaymentStatus'])

        if not m_payment.alreadyExists():
            m_payment.setOrderId(order['orderId'].split('!')[0])
            m_payment.setPaymentDate(payment['paymentDate'])
            m_payment.setUpdateDate(payment['paymentDate'])
            m_payment.setPaymentAmount(order['pricingSummary']['total']['value'])
            m_payment.setPaymentCurrency(order['pricingSummary']['total']['currency'])
            m_payment.setFeeAmount(0)
            m_payment.setFeeCurrency(order['pricingSummary']['total']['currency'])
            m_payment.add()

            payment_id = m_payment.getPaymentId()
            m_payment.addItems(items)
        else:
            payment_id = m_payment.getPaymentId()
            m_payment.updateItems(items)

        return payment_id

    def parseAddress(self, order_id, address) -> None:
        address = address['shippingStep']['shipTo']
        m_address = Address(self.db)
        m_address.setOrderId(order_id)
        m_address.setBuyerName(address['fullName'])
        m_address.setAddressLine1(address['contactAddress']['addressLine1'])
        m_address.setCity(address['contactAddress']['city'])

        try:
            m_address.setCounty(address['contactAddress']['stateOrProvince'])
        except KeyError:
            m_address.setCounty("")

        m_address.setPostCode(address['contactAddress']['postalCode'])
        m_address.setCountryCode(address['contactAddress']['countryCode'])

        if not m_address.alreadyExists():
            m_address.setId(m_address.add())

        m_address.addOrder()

    def parseRefund(self, payment_id, refund) -> None:
        m_refund = Refund(self.db)
        m_refund.setId(refund['refundId'])
        m_refund.setProcessorName('EBAY')

        if not m_refund.alreadyExists():
            m_refund.setDate(refund['refundDate'])
            m_refund.setOriginalPaymentId(payment_id)
            m_refund.setAmount(refund['amount']['value'])
            m_refund.setCurrency(refund['amount']['currency'])
            m_refund.setFee(0)
            m_refund.setFeeCurrency(refund['amount']['currency'])
            m_refund.add()
