#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime, timedelta

from .logger import Logger

@dataclass
class Sale():
    db: any
    order_id: str = None
    legacy_order_id: str = None
    buyer_username: str = None
    fee: float = None
    _status: str = None
    _sale_date: datetime = None
    _last_updated: datetime = None
    _valid: bool = True

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str) -> None:
        try:
            assert status in ("FULFILLED", "IN PROGRESS", "NOT STARTED")
            self._status = status
        except AssertionError:
            msg = (f"""Status '{status}' does not match an expected value """
                   f"""for order {self.order_id}.""")
            Logger.create_entry(message=msg, entry_type="error")
            self._valid = False

    @property
    def sale_date(self) -> datetime:
        return self._sale_date.strftime("%Y-%m-%d %H:%M:%S")

    @sale_date.setter
    def sale_date(self, date: str) -> None:
        try:
            self._sale_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            msg = (f"""Sale date '{date}' does not match the expected """
                   f"""format for order {self.order_id}.""")
            Logger.create_entry(message=msg, entry_type="error")
            self._valid = False

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    @last_updated.setter
    def last_updated(self, date: str) -> None:
        try:
            self._last_updated = datetime.strptime(
                date,
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except ValueError:
            msg = (f"""Last updated date '{date}' does not match the """
                   f"""expected format for order {self.order_id}.""")
            Logger.create_entry(message=msg, entry_type="error")
            self._valid = False

    @property
    def valid(self) -> bool:
        return self._valid

    def exists(self) -> bool:
        if not self.get_last_updated(self.db, self.order_id):
            return False

        return True

    def add(self) -> bool:
        query = self.db.cursor()

        try:
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
                )
            """, {
                'order_id': self.order_id,
                'legacy_order_id': self.legacy_order_id,
                'sale_date': self.sale_date,
                'buyer_username': self.buyer_username,
                'status': self.status,
                'fee': self.fee,
                'last_updated': self.last_updated
            })
        except self.db.OperationalError as error:
            msg = (f"""Unable to add sale record for order {self.order_id}. """
                   f"""Message: {error}.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True

    def update(self) -> bool:
        query = self.db.cursor()

        try:
            query.execute("""
                UPDATE sale
                SET
                    status = %(status)s,
                    last_updated = %(last_updated)s
                WHERE
                    order_id = %(order_id)s
            """, {
                'status': self.status,
                'last_updated': self.last_updated,
                'order_id': self.order_id
            })
        except self.db.OperationalError as error:
            msg = (f"""Unable to update sale record for order """
                   f"""{self.order_id}. Message: {error}.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True

    @staticmethod
    def get_last_updated(db, order_id: str) -> str:
        query = db.cursor()
        query.execute("""
            SELECT
                last_updated
            FROM
                sale 
            WHERE
                order_id = %(order_id)s
        """, {
            'order_id': order_id
        })

        return query.fetchone()

    @staticmethod
    def get_order_ids(db, days: int = None, legacy_ids: bool = False) -> list:
        query = db.cursor()

        if legacy_ids:
            query_str = "SELECT legacy_order_id FROM sale"
        else:
            query_str = "SELECT order_id FROM sale"

        if days:
            start_date = datetime.today() - timedelta(days=days)
            query_str += (f""" WHERE sale_date >= '"""
                          f"""{start_date.strftime("%Y-%m-%d %H:%M:%S")}'""")

        query.execute(query_str)
        return [item[0] for item in query.fetchall()]
