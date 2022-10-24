#!/usr/bin/env python3

from .lib.api_request import APIrequest
from .lib.refund import Refund
from .lib.payment import Payment
from .lib.logger import Logger

class GetFinances():
    scope = 'https://api.ebay.com/oauth/api_scope/sell.finances'

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials
        self.order_id = None
        self.content = None

    def fetch(self, order_id):
        self.order_id = order_id
        uri = ("""https://apiz.ebay.com/sell/finances/v1/transaction"""
               f"""?filter=orderId:{{{order_id}}}""")

        if access_token := APIrequest.get_access_token(
            self.scope,
            self.credentials.ebay_refresh_token,
            self.credentials.get_oauth_token()
        ):
            if content := APIrequest.get_rest_content(uri, access_token):
                self.content = content
                return self

        return None

    def parse(self):
        for transaction in self.content.get('transactions'):
            if (transaction_type := transaction.get('transactionType')) == 'SALE':
                self._parse_sale(transaction)
            elif transaction_type == 'REFUND':
                self._parse_refund(transaction)

    def _parse_sale(self, transaction: dict):
        payment = Payment(db=self.db)
        payment.order_id = self.order_id
        payment.processor_payment_id = self.order_id
        payment.transaction_date = transaction.get('transactionDate')
        payment.transaction_amount = transaction.get('totalFeeBasisAmount').get('value')
        payment.transaction_currency = transaction.get('totalFeeBasisAmount').get('currency')
        payment.fee_currency = transaction.get('totalFeeAmount').get('currency')

        if not payment.exists():
            payment.add()

        for item in transaction.get('orderLineItems'):
            line_item_id = item.get('lineItemId')
            if not payment.item_exists(line_item_id):
                payment.add_item(line_item_id)

    def _parse_refund(self, transaction: dict):
        if payment_id := Payment.get_id(db=self.db, order_id=self.order_id):
            refund = Refund(db=self.db)
            refund.original_payment_id = payment_id
            refund.processor_refund_id = transaction.get('references')[0].get('referenceId')
            refund.transaction_date = transaction.get('transactionDate')
            refund.amount = float(transaction.get('amount').get('value'))
            refund.currency = transaction.get('amount').get('currency')

            if fee := transaction.get('totalFeeAmount'):
                refund.fee = fee.get('value')
                refund.fee_currency = fee.get('currency')
                refund.amount += float(refund.fee)
            else:
                refund.fee = 0
                refund.fee_currency = refund.currency

            if not refund.exists():
                refund.add()
        else:
            msg = ("""Unable to find original payment record for order """
                   f"""'{self.order_id}'. Unable to add refund record.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True
