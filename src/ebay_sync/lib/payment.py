#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime

from .logger import Logger

@dataclass
class Payment():
    db: any
    payment_id: int = None
    order_id: str = None
    processor_name: str = 'EBAY'
    processor_payment_id: int = None
    transaction_amount: float = None
    transaction_currency: str = None
    fee_amount: float = 0
    fee_currency: str = None
    _transaction_date: datetime = None
    _valid: bool = True

    @property
    def transaction_date(self) -> datetime:
        return self._transaction_date.strftime("%Y-%m-%d %H:%M:%S")

    @transaction_date.setter
    def transaction_date(self, date: str) -> None:
        try:
            self._transaction_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            msg = (f"""Payment date '{date}' does not match the expected """
                   f"""format for payment '{self.processor_payment_id}'.""")
            Logger.create_entry(message=msg, entry_type="error")
            self._valid = False

    @property
    def valid(self) -> bool:
        return self._valid

    def add_items(self, items: dict) -> None:
        for item in items:
            query = self.db.cursor()
            query.execute("""
                INSERT INTO payment_items (
                    line_item_id,
                    payment_id
                ) VALUES (
                    %(line_item_id)s,
                    %(payment_id)s
                )
            """, {
                'line_item_id': item['line_item_id'],
                'payment_id': self.payment_id
            })

            self.db.commit()

    def exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                payment_id
            FROM
                payment
            WHERE
                processor_id = %(processor_id)s
            AND
                processor_name = %(processor_name)s
        """, {
            'processor_id': self.processor_payment_id,
            'processor_name': self.processor_name
        })

        self.payment_id = query.fetchone()

        if not self.payment_id:
            return False

        return True

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
                fee_currency
            ) VALUES (
                %(order_id)s,
                %(processor_name)s,
                %(processor_id)s,
                %(payment_date)s,
                %(payment_amount)s,
                %(payment_currency)s,
                %(fee_amount)s,
                %(fee_currency)s
            )
        """, {
            'order_id': self.order_id,
            'processor_name': self.processor_name,
            'processor_id': self.processor_payment_id,
            'payment_date': self.transaction_date,
            'payment_amount': self.transaction_amount,
            'payment_currency': self.transaction_currency,
            'fee_amount': self.fee_amount,
            'fee_currency': self.fee_currency
        })

        self.db.commit()
        self.payment_id = query.lastrowid
