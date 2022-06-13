#!/usr/bin/env python3

from datetime import datetime

class Fulfillment():
    def __init__(self, db):
        self.db = db

    def setFulfillmentId(self, value):
        self.fulfillment_id = value
        return self

    def setCarrier(self, value):
        self.carrier = value
        return self

    def setTrackingId(self, value):
        self.tracking_id = value
        return self

    def setFulfillmentDate(self, value):
        self.fulfillment_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def setLineItemIds(self, value):
        self.line_item_ids = value
        return self

    def add(self):
        query = self.db.cursor()

        if not hasattr(self, 'carrier'):
            self.carrier = None

        if not hasattr(self, 'fulfillment_date'):
            self.fulfillment_date = None

        query.execute("""
            INSERT IGNORE INTO fulfillment (
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

    def addLineItems(self):
        for item in self.line_item_ids:
            line_item_id = item['lineItemId']

            query = self.db.cursor()
            query.execute("""
                INSERT INTO line_fulfillment (
                    fulfillment_id,
                    line_item_id
                ) VALUES (
                    %(fulfillment_id)s,
                    %(line_item_id)s
                ) ON DUPLICATE KEY UPDATE
                    fulfillment_id = VALUES(fulfillment_id)
            """, {
                'fulfillment_id': self.fulfillment_id,
                'line_item_id': line_item_id
            })

            self.db.commit()
