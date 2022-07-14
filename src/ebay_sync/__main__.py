#!/usr/bin/env python3

import MySQLdb
import sys
import re

from .getFeedback import getFeedback
from .getFulfillment import getFulfillment
from .getSales import getSales
from .lib.sale import Sale
from .setup import setup
from .setup.credentials import Credentials

def credentials_setup(credentials):
    db_credentials = setup.getDbCredentials()

    while not setup.checkDbCredentials(db_credentials):
        db_credentials = setup.getDbCredentials()

    ebay_credentials = setup.getEbayAPICredentials()
    oauth_token = credentials.getOauthToken(
        ebay_credentials['app_id'],
        ebay_credentials['cert_id']
    )

    while not setup.checkEbayAPICredentials(
        ebay_credentials['refresh_token'],
        oauth_token
    ):
        ebay_credentials = setup.getEbayAPICredentials()

    config = {
        'client': db_credentials,
        'ebay': ebay_credentials
    }

    credentials.setConfig(config)
    credentials.saveConfigFile()

    print("")
    print("Credentials have been saved.")

def schema_setup(db_name: str):
    print("Installing database...")

    if not setup.installDb(db_name):
        print(
            """Unable to install database, check the specified user has the
            required privileges. Alternatively, load the included schema.sql
            file into your database."""
        )
    else:
        print("Database installed successfully.")

def getDbConnection(credentials):
    try:
        db = MySQLdb.connect(
            db=credentials.client_name,
            user=credentials.client_user,
            passwd=credentials.client_password
        )
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

    return db

def main():
    credentials = Credentials()

    if not credentials.readConfigFile():
        print("Config file not found, running setup...")

        while not credentials.readConfigFile():
            credentials_setup(credentials)

        schema_setup(credentials.client_name)

    db = getDbConnection()

    # Get sales
    sales = getSales(db, credentials)
    sales.fetch().parse()

    # Get Feedback
    legacy_order_ids = Sale.getLegacyOrderIds(db)
    for order_id in legacy_order_ids:
        if (re.match(r'[0-9]{12}-[0-9]{13}', str(order_id[0]))):
            getFeedback(db, credentials).fetch(order_id[0])

    # Get fulfillment info
    fulfillment = getFulfillment(db, credentials)
    for uri in sales.getFulfillmentLinks():
        fulfillment.setUri(uri).fetch().parse()

if __name__ == '__main__':
    sys.exit(main())
