#!/usr/bin/env python3

from datetime import datetime

class Transaction():
    def __init__(self, db):
        self.db = db

    def setOrderId(self, value):
        self.order_id = value
        return self 

    def setProcessorName(self, value):
        self.processor_name = value
        return self

    def setProcessorId(self, value):
        self.processor_id = value
        return self
        
    def setTransactionDate(self, value):                            
        self.transaction_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))
                                
        return self
        
    def setTransactionAmount(self, value):
        self.transaction_amount = value
        return self
    
    def setTransactionCurrency(self, value):
        self.transaction_currency = value
        return self
        
    def setFeeAmount(self, value):
        self.fee_amount = value
        return self
        
    def setFeeCurrency(self, value):
        self.fee_currency = value
        return self
        
    def setTransactionStatus(self, value):
        self.transaction_status = value
        return self

    def setUpdateDate(self, value):
        self.update_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))
                                
        return self

    def getTransactionId(self):
        if not self.transaction_id:
            return False
        
        return self.transaction_id

    def addItems(self, items: dict):
        for item in items:
            query = self.db.cursor()
            query.execute("""INSERT INTO payment_items (line_item_id,
                transaction_id, payment_status, currency, item_cost,
                postage_cost) VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE payment_status =
                VALUES(payment_status)""",
                (item['line_item_id'], self.transaction_id, self.transaction_status,
                item['currency'], item['cost'], item['postage_cost']))
            
            self.db.commit()

    def alreadyExists(self):
        query = self.db.cursor()
        query.execute("""SELECT processor_id, processor_name
                        FROM transaction
                        WHERE processor_id = %s
                        AND processor_name = %s""",
                        (self.processor_id, self.processor_name)
        )

        self.transaction_id = query.fetchone()

        if not self.transaction_id:
            return False

        return True           

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO transaction (order_id, processor_name, processor_id,
                        transaction_date, transaction_amount, transaction_currency,
                        fee_amount, fee_currency, transaction_status, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (self.order_id, self.processor_name, self.processor_id, self.transaction_date,
                        self.transaction_amount, self.transaction_currency, self.fee_amount,
                        self.fee_currency, 'S', self.update_date)
        )

        self.db.commit()
        self.transaction_id = query.lastrowid
