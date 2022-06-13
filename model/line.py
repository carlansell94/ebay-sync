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
        query.execute("""
            INSERT INTO line (
                line_item_id,
                order_id,
                item_id,
                title,
                sale_format,
                quantity,
                fulfillment_status
            ) VALUES (
                %(line_item_id)s,
                %(order_id)s,
                %(item_id)s,
                %(title)s,
                %(sale_format)s,
                %(quantity)s,
                %(fulfillment_status)s
            ) ON DUPLICATE KEY UPDATE
                fulfillment_status=VALUES(fulfillment_status)
        """, {
            'line_item_id': self.line_item_id,
            'order_id': self.order_id,
            'item_id': self.item_id,
            'title': self.title,
            'sale_format': self.sale_format,
            'quantity': self.quantity,
            'fulfillment_status': self.fulfillment_status
        })

        self.db.commit()
