#!/usr/bin/env python3

from datetime import datetime, timedelta

class Sale():
    def __init__(self, db) -> None:
        self.db = db
        self.order_id = None
        self.legacy_order_id = None
        self.sale_date = None
        self.buyer_username = None
        self.status = None
        self.fee = None
        self.last_updated = None

    def update_status(self, value: str) -> None:
        query = self.db.cursor()
        query.execute("""
            UPDATE sale
            SET status = %(value)s
            WHERE order_id = %(order_id)s
        """, {
            'status': value,
            'order_id': self.order_id
        })

    def set_order_id(self, value: str):
        self.order_id = value
        return self

    def set_legacy_order_id(self, value: str):
        self.legacy_order_id = value
        return self

    def set_sale_date(self, value: str):
        self.sale_date = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                            .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def set_buyer_username(self, value: str):
        self.buyer_username = value
        return self

    def set_status(self, value: str):
        self.status = value
        return self

    def set_fee(self, value):
        self.fee = value
        return self

    def set_last_updated(self, value: str):
        self.last_updated = (datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                                .strftime("%Y-%m-%d %H:%M:%S"))
        return self

    def add(self) -> None:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO sale (
                order_id,
                legacy_order_id,
                sale_date,
                buyer_username,
                status,
                sale_fee,
                last_updated
            ) VALUES (
                %(order_id)s,
                %(legacy_order_id)s,
                %(sale_date)s,
                %(buyer_username)s,
                %(status)s,
                %(fee)s,
                %(last_updated)s
            ) ON DUPLICATE KEY UPDATE
                status=VALUES(status),
                sale_fee=VALUES(sale_fee),
                last_updated=VALUES(last_updated)
        """, {
            'order_id': self.order_id,
            'legacy_order_id': self.legacy_order_id,
            'sale_date': self.sale_date,
            'buyer_username': self.buyer_username,
            'status': self.status,
            'fee': self.fee,
            'last_updated': self.last_updated
        })

        self.db.commit()

    @staticmethod
    def get_last_updated(db, order_id: str):
        query = db.cursor()
        query.execute("""SELECT
            last_updated
            FROM sale 
            WHERE order_id = %(order_id)s
        """, {
            'order_id': order_id
        })

        if query.rowcount == 0:
            return False

        return query.fetchall()

    @staticmethod
    def get_order_ids(db, days: int = None, legacy_ids: bool = False) -> list:
        query = db.cursor()

        if legacy_ids:
            query_string = "SELECT legacy_order_id FROM sale"
        else:
            query_string = "SELECT order_id FROM sale"

        if days:
            start_date = datetime.today() - timedelta(days=days)
            query_string += " WHERE sale_date >= '" + start_date.strftime("%Y-%m-%d %H:%M:%S") + "'"

        query.execute(query_string)
        return [item[0] for item in query.fetchall()]
