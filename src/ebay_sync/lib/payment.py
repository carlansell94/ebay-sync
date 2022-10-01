#!/usr/bin/env python3

from datetime import datetime

class Payment():
    def __init__(self, db) -> None:
        self.db = db
        self.payment_id = None
        self.order_id = None
        self.processor_name = None
        self.processor_id = None
        self.payment_date = None
        self.payment_amount = None
        self.payment_currency = None
        self.fee_amount = None
        self.fee_currency = None
        self.payment_status = None
        self.update_date = None

    def set_order_id(self, value: str):
        self.order_id = value
        return self

    def set_processor_name(self, value: str):
        self.processor_name = value
        return self

    def set_processor_id(self, value: str):
        self.processor_id = value
        return self

    def set_payment_date(self, value: str):
        self.payment_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))

        return self

    def set_payment_amount(self, value):
        self.payment_amount = value
        return self

    def set_payment_currency(self, value: str):
        self.payment_currency = value
        return self

    def set_fee_amount(self, value):
        self.fee_amount = value
        return self

    def set_fee_currency(self, value: str):
        self.fee_currency = value
        return self

    def set_payment_status(self, value: str):
        self.payment_status = value
        return self

    def set_update_date(self, value: str):
        self.update_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))

        return self

    def get_payment_id(self) -> int:
        if not self.payment_id:
            return False

        return self.payment_id

    def add_items(self, items: dict) -> None:
        for item in items:
            query = self.db.cursor()
            query.execute("""
                INSERT INTO payment_items (
                    line_item_id,
                    payment_id,
                    payment_status,
                    currency,
                    item_cost,
                    postage_cost
                ) VALUES (
                    %(line_item_id)s,
                    %(payment_id)s,
                    %(payment_status)s,
                    %(currency)s,
                    %(cost)s,
                    %(postage_cost)s
                )
            """, {
                'line_item_id': item['line_item_id'],
                'payment_id': self.payment_id,
                'payment_status': self.payment_status,
                'currency': item['currency'],
                'cost': item['cost'],
                'postage_cost': item['postage_cost']
            })

            self.db.commit()

    def already_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT payment_id
            FROM payment
            WHERE processor_id = %(processor_id)s
            AND processor_name = %(processor_name)s
        """, {
            'processor_id': self.processor_id,
            'processor_name': self.processor_name
        })

        self.payment_id = query.fetchone()

        if not self.payment_id:
            return False

        return True

    def update_items(self, items: dict) -> None:
        for item in items:
            query = self.db.cursor()
            query.execute("""
                UPDATE payment_items
                SET payment_status = %(payment_status)s
                WHERE payment_id = %(payment_id)s
                AND line_item_id = %(line_item_id)s
            """, {
                'payment_status': self.payment_status,
                'payment_id': self.payment_id,
                'line_item_id': item['line_item_id']
            })

            self.db.commit()

    def add(self) -> int:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO payment (
                order_id,
                processor_name,
                processor_id,
                payment_date,
                payment_amount,
                payment_currency,
                fee_amount,
                fee_currency,
                last_updated
            ) VALUES (
                %(order_id)s,
                %(processor_name)s,
                %(processor_id)s,
                %(payment_date)s,
                %(payment_amount)s,
                %(payment_currency)s,
                %(fee_amount)s,
                %(fee_currency)s,
                %(update_date)s
            )
        """, {
            'order_id': self.order_id,
            'processor_name': self.processor_name,
            'processor_id': self.processor_id,
            'payment_date': self.payment_date,
            'payment_amount': self.payment_amount,
            'payment_currency': self.payment_currency,
            'fee_amount': self.fee_amount,
            'fee_currency': self.fee_currency,
            'update_date': self.update_date
        })

        self.db.commit()
        self.payment_id = query.lastrowid
