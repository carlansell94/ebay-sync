#!/usr/bin/env python3

class Line():
    def __init__(self, db):
        self.db = db

    def setOrderId(self, value):
        self.order_id = value
        return self

    def setItemId(self, value):
        self.item_id = value
        return self

    def setLineItemId(self, value):
        self.line_item_id = value
        return self

    def setTitle(self, value):
        self.title = value
        return self

    def setSaleFormat(self, value):
        self.sale_format = value
        return self

    def setQuantity(self, value):
        self.quantity = value
        return self

    def setFulfillmentStatus(self, value):
        self.fulfillment_status = value
        return self

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO line (line_item_id, order_id, item_id,
                        title, sale_format, quantity, fulfillment_status)
                        VALUES(%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE
                        KEY UPDATE fulfillment_status=VALUES(fulfillment_status)""",
                        (self.line_item_id, self.order_id, self.item_id,
                            self.title, self.sale_format, self.quantity,
                            self.fulfillment_status
                        )
        )

        self.db.commit()
