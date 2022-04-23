#!/usr/bin/env python3

from datetime import datetime

class Payment():
    def __init__(self, db):
        self.db = db

    def setLineItemId(self, value):
        self.line_item_id = value
        return self

    def setPaymentDate(self, value):
        self.payment_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                                .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def setPaymentStatus(self, value):
        self.payment_status = value
        return self

    def setCurrency(self, value):
        self.currency = value
        return self

    def setItemCost(self, value):
        self.item_cost = value
        return self

    def setPostageCost(self, value):
        self.postage_cost = value
        return self
        
    def setTransactionId(self, value):
        self.transaction_id = value
        return self

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO payment (line_item_id, transaction_id,
                        payment_date, payment_status, currency, item_cost,
                        postage_cost) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE payment_status = VALUES(
                        payment_status)""",
                        (self.line_item_id, self.transaction_id,
                            self.payment_date, self.payment_status,
                            self.currency, self.item_cost, self.postage_cost
                        )
        )

        self.db.commit()
