#!/usr/bin/env python3

class Line():
    def __init__(self, db) -> None:
        self.db = db
        self.order_id = None
        self.item_id = None
        self.line_item_id = None
        self.title = None
        self.sale_format = None
        self.quantity = None
        self.fulfillment_status = None

    def set_order_id(self, value: str):
        self.order_id = value
        return self

    def set_item_id(self, value: int):
        self.item_id = value
        return self

    def set_line_item_id(self, value: int):
        self.line_item_id = value
        return self

    def set_title(self, value: str):
        self.title = value
        return self

    def set_sale_format(self, value: str):
        self.sale_format = value
        return self

    def set_quantity(self, value: int):
        self.quantity = value
        return self

    def set_fulfillment_status(self, value: str):
        self.fulfillment_status = value
        return self

    def add(self) -> None:
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
