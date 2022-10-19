#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime

from .logger import Logger

@dataclass
class Refund():
    db: any
    refund_id: int = None
    processor_name: str = 'EBAY'
    processor_refund_id: int = None
    original_payment_id: int = None
    amount: float = None
    currency: str = None
    fee: float = 0
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
            msg = (f"""Refund date '{date}' does not match the expected """
                   f"""format for refund '{self.processor_refund_id}'.""")
            Logger.create_entry(message=msg, entry_type="error")
            self._valid = False

    @property
    def valid(self) -> bool:
        return self._valid

    def exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                processor_id,
                processor_name
            FROM
                refund
            WHERE
                processor_id = %(processor_id)s
            AND
                processor_name = %(processor_name)s
        """, {
            'processor_id': self.processor_refund_id,
            'processor_name': self.processor_name
        })

        return query.fetchone()

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
            'processor_id': self.processor_refund_id,
            'original_payment_id': self.original_payment_id,
            'date': self.transaction_date,
            'amount': self.amount,
            'currency': self.currency,
            'fee': self.fee,
            'fee_currency': self.fee_currency
        })

        self.db.commit()
