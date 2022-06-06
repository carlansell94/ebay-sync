#!/usr/bin/env python3

import MySQLdb
import sys
import re
sys.path.append("..")

from core.credentials import Credentials
from model.sale import Sale
from model.fulfillment import Fulfillment
from sync.getSales import getSales
from sync.getFeedback import getFeedback
from sync.getFulfillment import getFulfillment

credentials = Credentials()
db = MySQLdb.connect(db=credentials.db_name, user=credentials.db_user,
                        passwd=credentials.db_password)

# Get sales
sales = getSales(db, credentials)
sales.fetch().parse()

# Get Feedback
sale = Sale(db)
legacy_order_ids = sale.getLegacyOrderIds()
for order_id in legacy_order_ids:
    if (re.match(r'[0-9]{12}-[0-9]{13}', str(order_id[0]))):
        getFeedback(db, credentials).fetch(order_id[0])

# Get fulfillment info
fulfillment = getFulfillment(credentials)

for link in sales.getFulfillmentLinks():
    out = fulfillment.setUri(link).fetch()
    f = Fulfillment(db)

    if out is None:
        tracking = link.rsplit('/', 1)[1]

        f.setFulfillmentId(tracking)
        f.setTrackingId(tracking)
        f.add()
    else:
        f.setFulfillmentId(out['fulfillmentId'])
        f.setCarrier(out['shippingCarrierCode'])
        f.setTrackingId(out['shipmentTrackingNumber'])
        f.setFulfillmentDate(out['shippedDate'])
        f.add()

        f.setLineItemIds(out['lineItems'])
        f.addLineItems()
