#!/usr/bin/env python3

from datetime import datetime

class Refund():
    def __init__(self, db) -> None:
        self.db = db
        self.processor_id = None
        self.processor_name = None
        self.original_payment_id = None
        self.date = None
        self.amount = None
        self.currency = None
        self.fee = None
        self.fee_currency = None

    def set_processor_id(self, value: int):
        self.processor_id = value
        return self

    def set_processor_name(self, value: str):
        self.processor_name = value
        return self

    def set_original_payment_id(self, value: int):
        self.original_payment_id = value
        return self

    def set_date(self, value: str):
        self.date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                        .strftime("%Y-%m-%d %H:%M:%S"))

        return self

    def set_amount(self, value):
        self.amount = value
        return self

    def set_currency(self, value: str):
        self.currency = value
        return self

    def set_fee(self, value):
        self.fee = value
        return self

    def set_fee_currency(self, value: str):
        self.fee_currency = value
        return self

    def already_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                processor_id,
                processor_name
            FROM refund
            WHERE processor_id = %(processor_id)s
            AND processor_name = %(processor_name)s
        """, {
            'processor_id': self.processor_id,
            'processor_name': self.processor_name
        })

        if query.fetchone():
            return True

        return False

    def add(self) -> None:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO refund (
                processor_name,
                processor_id,
                original_id,
                refund_date,
                refund_amount,
                refund_currency,
                fee_refund_amount,
                fee_refund_currency
            ) VALUES (
                %(processor_name)s,
                %(processor_id)s,
                %(original_payment_id)s,
                %(date)s,
                %(amount)s,
                %(currency)s,
                %(fee)s,
                %(fee_currency)s
            )
        """, {
            'processor_name': self.processor_name,
            'processor_id': self.processor_id,
            'original_payment_id': self.original_payment_id,
            'date': self.date,
            'amount': self.amount,
            'currency': self.currency,
            'fee': self.fee,
            'fee_currency': self.fee_currency
        })

        self.db.commit()
