#!/usr/bin/env python3

from core.sales import Sales
from model.sale import Sale
from model.line import Line
from model.payment import Payment
from model.fulfillment import Fulfillment
from datetime import datetime

class getSales:
    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self):
        sales = Sales(self.credentials)
        self.sales = sales.get()
        return self

    def syncNeeded(self):
        date = self.sale.last_updated
        last_updated = self.sale.getLastUpdated()

        if last_updated != False:
            last_updated = last_updated[0][0].strftime("%Y-%m-%d %H:%M:%S")

        if date == last_updated:
            return False

        return True

    def parse(self):
        for sale in self.sales['orders']:
            self.sale = Sale(self.db)
            self.line = Line(self.db)
            self.payment = Payment(self.db)
            self.fulfillment = Fulfillment(self.db)

            order_id = sale['orderId'].split('!')[0]
            self.sale.setOrderId(order_id)
            self.line.setOrderId(order_id)
            self.fulfillment.setOrderId(order_id)
            self.sale.setLastUpdated(sale['lastModifiedDate'])

            if self.syncNeeded():
                self.sale.setLegacyOrderId(sale['legacyOrderId'])
                self.sale.setSaleDate(sale['creationDate'])
                self.sale.setBuyerUsername(sale['buyer']['username'])
                self.sale.setStatus(sale['orderFulfillmentStatus'])
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
                    self.payment.setCurrency(line_items['lineItemCost']
                        ['convertedFromCurrency']
                    )
                    self.payment.setItemCost(line_items['lineItemCost']
                        ['convertedFromValue']
                    )
                    self.payment.setPostageCost(line_items['deliveryCost']
                        ['shippingCost']['convertedFromValue']
                    )

                for payment in sale['paymentSummary']['payments']:
                    self.payment.setPaymentId(payment['paymentReferenceId'])
                    self.payment.setPaymentDate(payment['paymentDate'])
                    self.payment.setPaymentStatus(payment['paymentStatus'])                
                    self.payment.add()

                for shipping in sale['fulfillmentStartInstructions']:
                    ship_to = shipping['shippingStep']['shipTo']
                    self.fulfillment.setBuyerName(ship_to['fullName'])
                    self.fulfillment.setAddressLine1(ship_to['contactAddress']
                        ['addressLine1']
                    )
                    self.fulfillment.setCity(ship_to['contactAddress']['city'])
                    self.fulfillment.setCounty(ship_to['contactAddress']
                        ['stateOrProvince']
                    )
                    self.fulfillment.setPostCode(ship_to['contactAddress']
                        ['postalCode']
                    )
                    self.fulfillment.setCountryCode(ship_to['contactAddress']
                        ['countryCode']
                    )
                    self.fulfillment.add()
