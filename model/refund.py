#!/usr/bin/env python3

from datetime import datetime

class Refund():
    def __init__(self, db) -> None:
        self.db = db      

    def setId(self, value: int):
        self.id = value
        return self

    def setProcessorName(self, value: str):
        self.processor_name = value
        return self

    def setOriginalPaymentId(self, value: int):
        self.original_payment_id = value
        return self

    def setDate(self, value: str):                            
        self.date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                        .strftime("%Y-%m-%d %H:%M:%S"))
                                
        return self

    def setAmount(self, value):
        self.amount = value
        return self

    def setCurrency(self, value: str):
        self.currency = value
        return self

    def setFee(self, value):
        self.fee = value
        return self

    def setFeeCurrency(self, value: str):
        self.fee_currency = value
        return self

    def alreadyExists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                processor_id,
                processor_name
            FROM refund
            WHERE processor_id = %(processor_id)s
            AND processor_name = %(processor_name)s
        """, {
            'processor_id': self.id,
            'processor_name': self.processor_name
        })

        self.payment_id = query.fetchone()

        if not self.payment_id:
            return False

        return True           

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
            'processor_id': self.id,
            'original_payment_id': self.original_payment_id,
            'date': self.date,
            'amount': self.amount,
            'currency': self.currency,
            'fee': self.fee,
            'fee_currency': self.fee_currency
        })

        self.db.commit()
