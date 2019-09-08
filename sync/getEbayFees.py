#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from core.xmlrequest import XMLRequest
from model.fee import Fee

class getEbayFees:
    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self):
        d = datetime.today() - timedelta(days=90)
        args = ('<IncludeFinalValueFee>true</IncludeFinalValueFee>'
                + '<CreateTimeFrom>'
                + d.strftime("%Y-%m-%dT%H:%M:%S.999Z")
                + '</CreateTimeFrom><CreateTimeTo>'
                + datetime.today().strftime("%Y-%m-%dT%H:%M:%S.999Z")
                + '</CreateTimeTo><OutputSelector>FinalValueFee'
                + '</OutputSelector><OutputSelector>OrderId</OutputSelector>'
        )

        req = XMLRequest()
        res = req.getRequest('GetOrders', args)
        root = ET.fromstring(res)

        fee = Fee(self.db)

        for order in root.iter(tag='{urn:ebay:apis:eBLBaseComponents}Order'):
            for ID in order.iter(tag='{urn:ebay:apis:eBLBaseComponents}OrderID'):
                fee.setOrderId(ID.text)

            for FVF in order.iter(tag='{urn:ebay:apis:eBLBaseComponents}FinalValueFee'):
                fee.setFinalValueFee(float(FVF.text) * 1.2)

            fee.addEbayFee()
