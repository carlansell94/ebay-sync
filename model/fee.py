#!/usr/bin/env python3

class Fee():
    def __init__(self, db):
        self.db = db

    def setOrderId(self, value):
        self.order_id = value
        return self

    def setFinalValueFee(self, value):
        self.final_value_fee = value
        return self

    def addEbayFee(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO fee (order_id, final_value_fee)
                        VALUES(%s, %s) ON DUPLICATE KEY UPDATE
                        final_value_fee=VALUES(final_value_fee)""",
                        (self.order_id, self.final_value_fee)
        )

        self.db.commit()
