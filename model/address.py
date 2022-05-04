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
        query.execute("""SELECT address_id
                        FROM addresses
                        WHERE buyer_name = %s
                        AND address_line_1 = %s
                        AND post_code = %s""",
                        (self.buyer_name, self.address_line_1, self.post_code)
        )

        self.address_id = query.fetchone()

        if not self.address_id:
            return False

        return True

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO addresses (buyer_name,
                        address_line_1, city, county, post_code, country_code)
                        VALUES(%s, %s, %s, %s, %s, %s)""",
                        (self.buyer_name, self.address_line_1,
                            self.city, self.county, self.post_code,
                            self.country_code
                        )
        )

        self.db.commit()

        return query.lastrowid

    def addOrder(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO sale_address (order_id, address_id)
                        VALUES(%s, %s)""",
                        (self.order_id, self.address_id)
        )
