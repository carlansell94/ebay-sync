#!/usr/bin/env python3

from datetime import datetime

class Sale():
    def __init__(self, db):
        self.db = db

    def getLegacyOrderIds(self):
        query = self.db.cursor()
        query.execute("SELECT legacy_order_id FROM sale")
        return query.fetchall()

    def updateStatus(self, value):
        query = self.db.cursor()
        query.execute("UPDATE sale SET status = %s WHERE order_id = %s",
                        (value, self.order_id)
        )

    def setOrderId(self, value):
        self.order_id = value
        return self

    def setLegacyOrderId(self, value):
        self.legacy_order_id = value
        return self

    def setSaleDate(self, value):
        self.sale_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def setBuyerUsername(self, value):
        self.buyer_username = value
        return self

    def setStatus(self, value):
        self.status = value
        return self

    def setFee(self, value):
        self.fee = value
        return self

    def setLastUpdated(self, value):
        self.last_updated = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                                .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO sale (order_id, legacy_order_id, sale_date,
                        buyer_username, status, sale_fee, last_updated) VALUES
                        (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE
                        status=VALUES(status), sale_fee=VALUES(sale_fee),
                        last_updated=VALUES(last_updated)""",
                        (self.order_id, self.legacy_order_id, self.sale_date,
                            self.buyer_username, self.status, self.fee, self.last_updated
                        )
        )

        self.db.commit()

    @staticmethod
    def getLastUpdated(db, order_id):
        query = db.cursor()
        query.execute(f"SELECT last_updated FROM sale WHERE order_id = '{order_id}'")

        if query.rowcount == 0:
            return False

        return query.fetchall()
