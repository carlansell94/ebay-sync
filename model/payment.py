#!/usr/bin/env python3

from datetime import datetime

class Payment():
    def __init__(self, db):
        self.db = db

    def setOrderId(self, value):
        self.order_id = value
        return self

    def setLineItemId(self, value):
        self.line_item_id = value
        return self

    def setPaymentId(self, value):
        self.payment_id = value
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

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO payment VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (self.line_item_id, self.order_id, self.payment_id,
                            self.payment_date, self.payment_status,
                            self.currency, self.item_cost, self.postage_cost
                        )
        )

        self.db.commit()
