#!/usr/bin/env python3

from datetime import datetime

class Payment():
    def __init__(self, db):
        self.db = db

    def setOrderId(self, value):
        self.order_id = value
        return self 

    def setProcessorName(self, value):
        self.processor_name = value
        return self

    def setProcessorId(self, value):
        self.processor_id = value
        return self

    def setPaymentDate(self, value):                            
        self.payment_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))

        return self

    def setPaymentAmount(self, value):
        self.payment_amount = value
        return self

    def setPaymentCurrency(self, value):
        self.payment_currency = value
        return self

    def setFeeAmount(self, value):
        self.fee_amount = value
        return self

    def setFeeCurrency(self, value):
        self.fee_currency = value
        return self

    def setPaymentStatus(self, value):
        self.payment_status = value
        return self

    def setUpdateDate(self, value):
        self.update_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))

        return self

    def getPaymentId(self):
        if not self.payment_id:
            return False

        return self.payment_id

    def addItems(self, items: dict):
        for item in items:
            query = self.db.cursor()
            query.execute("""INSERT INTO payment_items (line_item_id,
                payment_id, payment_status, currency, item_cost,
                postage_cost) VALUES (%s, %s, %s, %s, %s, %s)""",
                (item['line_item_id'], self.payment_id, self.payment_status,
                item['currency'], item['cost'], item['postage_cost']))

            self.db.commit()

    def alreadyExists(self):
        query = self.db.cursor()
        query.execute("""SELECT payment_id
                        FROM payment
                        WHERE processor_id = %s
                        AND processor_name = %s""",
                        (self.processor_id, self.processor_name)
        )

        self.payment_id = query.fetchone()

        if not self.payment_id:
            return False

        return True

    def updateItems(self, items):
        for item in items:
            query = self.db.cursor()
            query.execute("""UPDATE payment_items
                            SET payment_status = %s
                            WHERE payment_id = %s
                            AND line_item_id = %s""",
                            (self.payment_status, self.payment_id, item['line_item_id'])
            )

            self.db.commit()

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO payment (order_id, processor_name, processor_id,
                        payment_date, payment_amount, payment_currency,
                        fee_amount, fee_currency, payment_status, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (self.order_id, self.processor_name, self.processor_id, self.payment_date,
                        self.payment_amount, self.payment_currency, self.fee_amount,
                        self.fee_currency, 'S', self.update_date)
        )

        self.db.commit()
        self.payment_id = query.lastrowid
