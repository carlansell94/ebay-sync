#!/usr/bin/env python3

class Address():
    def __init__(self, db):
        self.db = db

    def setId(self, value):
        self.address_id = value
        return self

    def setOrderId(self, value):
        self.order_id = value
        return self

    def setBuyerName(self, value):
        self.buyer_name = value
        return self

    def setAddressLine1(self, value):
        self.address_line_1 = value
        return self

    def setCity(self, value):
        self.city = value
        return self

    def setCounty(self, value):
        self.county = value
        return self

    def setPostCode(self, value):
        self.post_code = value
        return self

    def setCountryCode(self, value):
        self.country_code = value
        return self

    def alreadyExists(self):
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

        address_id = query.fetchone()

        if not address_id:
            return False
        else:
            self.address_id = address_id[0]

        return True

    def add(self):
        query = self.db.cursor()
        query.execute("""
            INSERT INTO addresses (
                buyer_name,
                address_line_1,
                city,
                county,
                post_code,
                country_code
            ) VALUES (
                %(buyer_name)s,
                %(address_line_1)s,
                %(city)s,
                %(county)s,
                %(post_code)s,
                %(country_code)s
            )
        """, {
            'buyer_name': self.buyer_name,
            'address_line_1': self.address_line_1,
            'city': self.city,
            'county': self.county,
            'post_code': self.post_code,
            'country_code': self.country_code
        })

        self.db.commit()

        return query.lastrowid

    def addOrder(self):
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
