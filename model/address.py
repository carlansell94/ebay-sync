#!/usr/bin/env python3

class Address():
    def __init__(self, db):
        self.db = db

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

    def add(self):
        query = self.db.cursor()
        query.execute("""INSERT INTO addresses (order_id, buyer_name,
                        address_line_1, city, county, post_code, country_code)
                        VALUES(%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                        UPDATE order_id = VALUES(order_id)""",
                        (self.order_id, self.buyer_name, self.address_line_1,
                            self.city, self.county, self.post_code,
                            self.country_code
                        )
        )

        self.db.commit()
