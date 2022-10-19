#!/usr/bin/env python3

from dataclasses import dataclass

from .logger import Logger

@dataclass
class Line():
    db: any
    order_id: str = None
    item_id: int = None
    line_item_id: int = None
    title: str = None
    sale_format: str = None
    quantity: int = None
    fulfillment_status: str = None

    def exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                order_id
            FROM
                line 
            WHERE
                order_id = %(order_id)s
        """, {
            'order_id': self.order_id
        })

        return query.fetchone()

    def add(self) -> bool:
        query = self.db.cursor()

        try:
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
                )
            """, {
                'line_item_id': self.line_item_id,
                'order_id': self.order_id,
                'item_id': self.item_id,
                'title': self.title,
                'sale_format': self.sale_format,
                'quantity': self.quantity,
                'fulfillment_status': self.fulfillment_status
            })
        except self.db.OperationalError as error:
            msg = (f"""Unable to add line record for order {self.order_id}. """
                   f"""Message: {error}.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True

    def update(self) -> bool:
        query = self.db.cursor()

        try:
            query.execute("""
                UPDATE line
                SET
                    fulfillment_status = %(fulfillment_status)s
                WHERE
                    order_id = %(order_id)s
            """, {
                'fulfillment_status': self.fulfillment_status,
                'order_id': self.order_id
            })
        except self.db.OperationalError as error:
            msg = (f"""Unable to update line record for order """
                   f"""{self.order_id}. Message: {error}.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True
