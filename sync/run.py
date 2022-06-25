#!/usr/bin/env python3

import MySQLdb
import sys
import re

sys.path.append("..")

from core.credentials import Credentials
from model.sale import Sale
from setup import setup
from sync.getSales import getSales
from sync.getFeedback import getFeedback
from sync.getFulfillment import getFulfillment

def runSetup(credentials):
    db_credentials = setup.getDbCredentials()
    
    while not setup.checkDbCredentials(db_credentials):
        db_credentials = setup.getDbCredentials()
    
    ebay_credentials = setup.getEbayAPICredentials()
    oauth_token = credentials.getOauthToken(ebay_credentials['app_id'], ebay_credentials['cert_id'])

    while not setup.checkEbayAPICredentials(ebay_credentials, oauth_token):
        ebay_credentials = setup.getEbayAPICredentials()
    
    config = {
        'client': db_credentials,
        'ebay': ebay_credentials
    }

    credentials.setConfig(config)
    credentials.saveConfigFile()

    print("")
    print("Credentials have been saved.")
    print("Installing database...")

    if setup.installDb(db_credentials['name']) == False:
        print("Unable to install database, check the specified user has the required privileges.")
        print("Alternatively, load the included schema.sql file into your database.")
    else:
        print("Database installed successfully.")

def main():
    credentials = Credentials()

    if not credentials.readConfigFile():
        print("Config file not found, running setup...")
        runSetup(credentials)

    db = MySQLdb.connect(db=credentials.client_name, user=credentials.client_user,
                            passwd=credentials.client_password)

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
    fulfillment = getFulfillment(db, credentials)
    for uri in sales.getFulfillmentLinks():
        fulfillment.setUri(uri).fetch().parse()

if __name__ == '__main__':
    sys.exit(main())
