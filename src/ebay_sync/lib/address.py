#!/usr/bin/env python3

class Address():
    def __init__(self, db) -> None:
        self.db = db
        self.address_id = None
        self.order_id = None
        self.buyer_name = None
        self.address_line_1 = None
        self.address_line_2 = None
        self.city = None
        self.county = None
        self.post_code = None
        self.country_code = None

    def set_id(self, value: int):
        self.address_id = value
        return self

    def set_order_id(self, value: str):
        self.order_id = value
        return self

    def set_buyer_name(self, value: str):
        self.buyer_name = value
        return self

    def set_address_line_1(self, value: str):
        self.address_line_1 = value
        return self

    def set_address_line_2(self, value: str):
        self.address_line_2 = value
        return self

    def set_city(self, value: str):
        self.city = value
        return self

    def set_county(self, value: str):
        self.county = value
        return self

    def set_post_code(self, value: str):
        self.post_code = value
        return self

    def set_country_code(self, value: str):
        self.country_code = value
        return self

    def already_exists(self) -> bool:
        query = self.db.cursor()
        query.execute("""
            SELECT address_id
            FROM addresses
            WHERE buyer_name = %(buyer_name)s
            AND address_line_1 = %(address_line_1)s
            AND post_code = %(post_code)s
        """, {
            'buyer_name': self.buyer_name,
            'address_line_1': self.address_line_1,
            'post_code': self.post_code
        })

        if address_id := query.fetchone():
            self.address_id = address_id[0]
            return True

        return False

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
