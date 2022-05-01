#!/usr/bin/env python3

from datetime import datetime

class Refund():
    def __init__(self, db):
        self.db = db      
    
    def setId(self, value):
        self.id = value
        return self
    
    def setProcessorName(self, value):
        self.processor_name = value
        return self
    
    def setOriginalTransactionId(self, value):
        self.original_transaction_id = value
        return self
        
    def setDate(self, value):                            
        self.date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                        .strftime("%Y-%m-%d %H:%M:%S"))
                                
        return self
        
    def setAmount(self, value):
        self.amount = value
        return self
    
    def setCurrency(self, value):
        self.currency = value
        return self
    
    def setFee(self, value):
        self.fee = value
        return self
    
    def setFeeCurrency(self, value):
        self.fee_currency = value
        return self
        
    def alreadyExists(self):
        query = self.db.cursor()
        query.execute("""SELECT processor_id, processor_name
                        FROM refund
                        WHERE processor_id = %s
                        AND processor_name = %s""",
                        (self.id, self.processor_name)
        )

        self.transaction_id = query.fetchone()

        if not self.transaction_id:
            return False

        return True           

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO refund (processor_name, processor_id, original_id,
                        refund_date, refund_amount, refund_currency,
                        fee_refund_amount, fee_refund_currency)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (self.processor_name, self.id, self.original_transaction_id, self.date,
                        self.amount, self.currency, self.fee, self.fee_currency)
        )

        self.db.commit()
