#!/usr/bin/env python3

from dataclasses import dataclass

@dataclass
class Address():
    db: any
    address_id: int = None
    order_id: str = None
    buyer_name: str = None
    address_line_1: str = None
    address_line_2: str = None
    city: str = None
    county: str = None
    post_code: str = None
    country_code: str = None

    def exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                address_id
            FROM
                addresses
            WHERE
                buyer_name = %(buyer_name)s
            AND
                address_line_1 = %(address_line_1)s
            AND
                post_code = %(post_code)s
        """, {
            'buyer_name': self.buyer_name,
            'address_line_1': self.address_line_1,
            'post_code': self.post_code
        })

        if address_id := query.fetchone():
            self.address_id = address_id[0]
            return True

        return False

    def order_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT
                order_id
            FROM
                sale_address
            WHERE
                order_id = %(order_id)s
            AND
                address_id = %(address_id)s
        """, {
            'order_id': self.order_id,
            'address_id': self.address_id
        })

        return query.fetchone()

    def add(self) -> int:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO addresses (
                buyer_name,
                address_line_1,
                address_line_2,
                city,
                county,
                post_code,
                country_code
            ) VALUES (
                %(buyer_name)s,
                %(address_line_1)s,
                %(address_line_2)s,
                %(city)s,
                %(county)s,
                %(post_code)s,
                %(country_code)s
            )
        """, {
            'buyer_name': self.buyer_name,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'county': self.county,
            'post_code': self.post_code,
            'country_code': self.country_code
        })

        self.db.commit()

        return query.lastrowid

    def add_order(self) -> None:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO sale_address (
                order_id,
                address_id
            ) VALUES (
                %(order_id)s,
                %(address_id)s
            )
        """, {
            'order_id': self.order_id,
            'address_id': self.address_id
        })

        self.db.commit()
