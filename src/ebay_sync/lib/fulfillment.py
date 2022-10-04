#!/usr/bin/env python3

from datetime import datetime

class Fulfillment():
    def __init__(self, db) -> None:
        self.db = db
        self.fulfillment_id = None
        self.carrier = None
        self.tracking_id = None
        self.fulfillment_date = None
        self.line_item_id = None

    def set_fulfillment_id(self, value: int):
        self.fulfillment_id = value
        return self

    def set_carrier(self, value: str):
        self.carrier = value
        return self

    def set_tracking_id(self, value: str):
        self.tracking_id = value
        return self

    def set_fulfillment_date(self, value: str):
        self.fulfillment_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def set_line_item_id(self, value: int):
        self.line_item_id = value
        return self

    def already_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                fulfillment_id
            FROM
                fulfillment
            WHERE
                fulfillment_id = %(fulfillment_id)s
        """, {
            'fulfillment_id': self.fulfillment_id
        })

        if query.fetchone():
            return True

        return False

    def line_item_already_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                fulfillment_id
            FROM
                line_fulfillment
            WHERE
                fulfillment_id = %(fulfillment_id)s
            AND
                line_item_id = %(line_item_id)s
        """, {
            'fulfillment_id': self.fulfillment_id,
            'line_item_id': self.line_item_id
        })

        if query.fetchone():
            return True

        return False

    def add(self) -> None:
        query = self.db.cursor()

        if not hasattr(self, 'carrier'):
            self.carrier = None

        if not hasattr(self, 'fulfillment_date'):
            self.fulfillment_date = None

        query.execute("""
            INSERT INTO fulfillment (
                fulfillment_id,
                carrier,
                tracking_id,
                fulfillment_date
            ) VALUES (
                %(fulfillment_id)s,
                %(carrier)s,
                %(tracking_id)s,
                %(fulfillment_date)s
            )
        """, {
            'fulfillment_id': self.fulfillment_id,
            'carrier': self.carrier,
            'tracking_id': self.tracking_id,
            'fulfillment_date': self.fulfillment_date
        })

        self.db.commit()

    def add_line_item(self) -> None:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO line_fulfillment (
                fulfillment_id,
                line_item_id
            ) VALUES (
                %(fulfillment_id)s,
                %(line_item_id)s
            )
        """, {
            'fulfillment_id': self.fulfillment_id,
            'line_item_id': self.line_item_id
        })

        self.db.commit()
