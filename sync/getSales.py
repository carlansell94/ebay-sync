#!/usr/bin/env python3

from model.sale import Sale
from model.line import Line
from model.payment import Payment
from model.address import Address
from model.transaction import Transaction
from model.refund import Refund
from datetime import datetime
from urllib.request import Request, urlopen
from urllib import parse
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

    def syncNeeded(self):
        date = self.sale.last_updated
        last_updated = self.sale.getLastUpdated()

        if last_updated != False:
            last_updated = last_updated[0][0].strftime("%Y-%m-%d %H:%M:%S")

        if date == last_updated:
            return False

        return True

    def getFulfillmentLinks(self):
        fulfillmentLinks = []

        for sale in self.sales['orders']:
            for fulfillment_link in sale['fulfillmentHrefs']:
                fulfillmentLinks.append(fulfillment_link)

        return fulfillmentLinks

    def parse(self):
        for sale in self.sales['orders']:
            self.sale = Sale(self.db)
            self.line = Line(self.db)
            self.payment = Payment(self.db)
            self.address = Address(self.db)
            self.transaction = Transaction(self.db)
            self.refund = Refund(self.db)

            order_id = sale['orderId'].split('!')[0]
            self.sale.setOrderId(order_id)
            self.line.setOrderId(order_id)
            self.address.setOrderId(order_id)
            self.sale.setLastUpdated(sale['lastModifiedDate'])

            if self.syncNeeded():
                self.sale.setLegacyOrderId(sale['legacyOrderId'])
                self.sale.setSaleDate(sale['creationDate'])
                self.sale.setBuyerUsername(sale['buyer']['username'])
                self.sale.setStatus(sale['orderFulfillmentStatus'])
                self.sale.setFee(sale['totalMarketplaceFee']['value'])
                self.sale.add()

                for line_items in sale['lineItems']:
                    self.line_item_id = line_items['lineItemId']
                    self.line.setItemId(line_items['legacyItemId'])
                    self.line.setLineItemId(self.line_item_id)
                    self.line.setTitle(line_items['title'])
                    self.line.setSaleFormat(line_items['soldFormat'])
                    self.line.setQuantity(line_items['quantity'])
                    self.line.setFulfillmentStatus(line_items
                        ['lineItemFulfillmentStatus']
                    )
                    self.line.add()

                    self.payment.setLineItemId(self.line_item_id)
                    self.payment.setCurrency(line_items['lineItemCost']['currency'])
                    self.payment.setItemCost(line_items['lineItemCost']['value'])
                    self.payment.setPostageCost(line_items['deliveryCost']
                        ['shippingCost']['value']
                    )

                for payment in sale['paymentSummary']['payments']:
                    self.transaction.setProcessorName(payment['paymentMethod'])
                    self.transaction.setProcessorId(sale['salesRecordReference'])
                    self.transaction.setTransactionDate(payment['paymentDate'])
                    self.transaction.setUpdateDate(payment['paymentDate'])
                    self.transaction.setTransactionAmount(sale['pricingSummary']['total']['value'])
                    self.transaction.setTransactionCurrency(sale['pricingSummary']['total']['currency'])
                    self.transaction.setFeeAmount(0)
                    self.transaction.setFeeCurrency(sale['pricingSummary']['total']['currency'])
                    self.transaction.setTransactionStatus('S')

                    if self.transaction.alreadyExists():
                        self.payment.setTransactionId(self.transaction.getTransactionId())
                    else:
                        self.payment.setTransactionId(self.transaction.add())

                    self.payment.setPaymentDate(payment['paymentDate'])
                    self.payment.setPaymentStatus(sale['orderPaymentStatus'])
                    self.payment.add()

                for refund in sale['paymentSummary']['refunds']:
                    self.refund.setId(refund['refundId'])
                    self.refund.setDate(refund['refundDate'])
                    self.refund.setProcessorName('EBAY')
                    self.refund.setOriginalTransactionId(self.transaction.getTransactionId())
                    self.refund.setAmount(refund['amount']['value'])
                    self.refund.setCurrency(refund['amount']['currency'])
                    self.refund.setFee(0)
                    self.refund.setFeeCurrency(refund['amount']['currency'])

                    if not self.refund.alreadyExists():
                        self.refund.add()

                for shipping in sale['fulfillmentStartInstructions']:
                    ship_to = shipping['shippingStep']['shipTo']
                    self.address.setBuyerName(ship_to['fullName'])
                    self.address.setAddressLine1(ship_to['contactAddress']
                        ['addressLine1']
                    )
                    self.address.setCity(ship_to['contactAddress']['city'])

                    try:
                        self.address.setCounty(ship_to['contactAddress']['stateOrProvince'])
                    except KeyError:
                        self.address.setCounty("")

                    self.address.setPostCode(ship_to['contactAddress']
                        ['postalCode']
                    )
                    self.address.setCountryCode(ship_to['contactAddress']
                        ['countryCode']
                    )
