#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime

from .logger import Logger

@dataclass
class Fulfillment():
    db: any
    fulfillment_id: int = None
    carrier: str = None
    tracking_id: str = None
    line_item_id: int = None
    _fulfillment_date: datetime = None
    _valid: bool = True

    @property
    def fulfillment_date(self) -> datetime:
        return self._fulfillment_date.strftime("%Y-%m-%d %H:%M:%S")

    @fulfillment_date.setter
    def fulfillment_date(self, date: str) -> None:
        try:
            self._fulfillment_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            msg = (f"""Fulfillment date '{date}' does not match the """
                   f"""expected format for id {self.fulfillment_id}.""")
            Logger.create_entry(message=msg, entry_type="error")
            self._valid = False

    @property
    def valid(self) -> bool:
        return self._valid

    def exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                fulfillment_id
            FROM
                fulfillment
            WHERE
                fulfillment_id = %(fulfillment_id)s
        """, {
            'fulfillment_id': self.fulfillment_id
        })

        return query.fetchone()

    def line_item_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                fulfillment_id
            FROM
                line_fulfillment
            WHERE
                fulfillment_id = %(fulfillment_id)s
            AND
                line_item_id = %(line_item_id)s
        """, {
            'fulfillment_id': self.fulfillment_id,
            'line_item_id': self.line_item_id
        })

        return query.fetchone()

    def add(self) -> None:
        query = self.db.cursor()

        query.execute("""
            INSERT INTO fulfillment (
                fulfillment_id,
                carrier,
                tracking_id,
                fulfillment_date
            ) VALUES (
                %(fulfillment_id)s,
                %(carrier)s,
                %(tracking_id)s,
                %(fulfillment_date)s
            )
        """, {
            'fulfillment_id': self.fulfillment_id,
            'carrier': self.carrier,
            'tracking_id': self.tracking_id,
            'fulfillment_date': self.fulfillment_date
        })

        self.db.commit()

    def add_line_item(self) -> None:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO line_fulfillment (
                fulfillment_id,
                line_item_id
            ) VALUES (
                %(fulfillment_id)s,
                %(line_item_id)s
            )
        """, {
            'fulfillment_id': self.fulfillment_id,
            'line_item_id': self.line_item_id
        })

        self.db.commit()
