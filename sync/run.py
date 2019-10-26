#!/usr/bin/env python3

import MySQLdb
import sys
import re
sys.path.append("..")

from datetime import datetime, timedelta
from core.credentials import Credentials
from model.feedback import Feedback
from model.sale import Sale
from sync.getSales import getSales
from sync.getFeedback import getFeedback
from sync.getEbayFees import getEbayFees

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

# Get eBay Fees
ebay_fees = getEbayFees(db, credentials).fetch()
