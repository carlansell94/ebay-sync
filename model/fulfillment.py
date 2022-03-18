#!/usr/bin/env python3
from datetime import datetime
import json

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
        query.execute("""INSERT IGNORE INTO fulfillment (fulfillment_id, carrier,
                        tracking_id, fulfillment_date)
                        VALUES(%s, %s, %s, %s)""",
                        (self.fulfillment_id, self.carrier, self.tracking_id, self.fulfillment_date)
        )

        self.db.commit()

    def addLineItems(self):
        for item in self.line_item_ids:
            line_item_id = item['lineItemId']

            query = self.db.cursor()
            query.execute("""INSERT INTO line_fulfillment (fulfillment_id, line_item_id)
                            VALUES(%s, %s)""",
                            (self.fulfillment_id, line_item_id))

            self.db.commit()
