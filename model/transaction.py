#!/usr/bin/env python3

from datetime import datetime

class Transaction():
    def __init__(self, db):
        self.db = db      
        
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
        
    def alreadyExists(self):
        query = self.db.cursor()
        query.execute("""SELECT processor_id, processor_name
                        FROM transaction
                        WHERE processor_id = %s
                        AND processor_name = %s""",
                        (self.processor_id, self.processor_name)
        )
        
        transaction = query.fetchone()  

        if not msg:
            return False
            
        return True           

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO transaction (processor_name, processor_id,
                        transaction_date, transaction_amount, transaction_currency,
                        fee_amount, fee_currency, transaction_status, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (self.processor_name, self.processor_id,self.transaction_date,
                        self.transaction_amount, self.transaction_currency, self.fee_amount,
                        self.fee_currency, self.transaction_status, self.update_date)
        )

        self.db.commit()
        
        return query.lastrowid
