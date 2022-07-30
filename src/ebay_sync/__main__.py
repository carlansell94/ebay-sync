#!/usr/bin/env python3

import MySQLdb
import sys
import re
import argparse

from .getFeedback import getFeedback
from .getFulfillment import getFulfillment
from .getSales import getSales
from .lib.sale import Sale
from .setup import setup
from .setup.credentials import Credentials

def getArgs():
    parser = argparse.ArgumentParser(
        prog="ebay_sync",
        description='Sync sales data from eBay using the eBay developer API'
    )

    parser_setup = parser.add_mutually_exclusive_group(required=False)
    parser_setup.add_argument("-s", "--setup", action='store_true',
        help="Set database/api credentials and install the database")
    parser_setup.add_argument("-c", "--credentials", action='store_true',
        help="Set new database/api credentials")
    parser_setup.add_argument("-i", "--install", action='store_true',
        help="Install the database schema")
    parser_setup.add_argument("-r", "--refresh-token",
        help="Fetch a new refresh token using the provided auth URL")
    parser_setup.add_argument("-t", "--test", action='store_true',
        help="Test the database/api credentials")

    return parser.parse_args()

def run_setup(credentials, args):
    if args.credentials:
        setup.credentialsSetup(credentials)
        exit()

    if args.install:
        db = getDbConnection(credentials)

        if not db:
            print(
                """Please run 'ebay_sync -s' or 'ebay_sync -c to """
                """create a new credentials file."""
            )
            exit()
        
        if not setup.installDb(db, credentials.client_name):
            print(
                """Unable to install database, check the specified user """
                """has the required privileges. Alternatively, load the """
                """included schema.sql file into your database."""
            )
        else:
            print("Database installed successfully.")

        exit()

    if args.test:
        if setup.checkAllCredentials(credentials):
            print("Test completed successfully, credentials are valid.")
        else:
            print(
                """Errors found, please run ebay_sync -s or ebay_sync -c """
                """to create a new credentials file."""
            )
        exit()

    if args.refresh_token is not None:
        oauth_token = credentials.getOauthToken(
            credentials.ebay_app_id,
            credentials.ebay_cert_id
        )

        new_refresh_token = setup.getNewRefreshToken(
            args.refresh_token,
            oauth_token,
            credentials.ebay_redirect_url
        )

        if new_refresh_token:
            credentials.setOptionValue(
                'ebay_refresh_token',
                new_refresh_token
            )
            credentials.saveConfigFile()

            print("eBay API refresh token has been updated successfully.")
        else:
            print(
                """Unable to fetch a new refresh token, check the """
                """provided return URL is valid."""
            )

        exit()

def runSync(credentials):
    db = getDbConnection(credentials)

    sales = getSales(db, credentials)
    sales.fetch().parse()

    fulfillment = getFulfillment(db, credentials)
    for uri in sales.getFulfillmentLinks():
        fulfillment.setUri(uri).fetch().parse()

    legacy_order_ids = Sale.getLegacyOrderIds(db)
    for order_id in legacy_order_ids:
        if (re.match(r'[0-9]{12}-[0-9]{13}', str(order_id[0]))):
            getFeedback(db, credentials).fetch(order_id[0])

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
    credentials_loaded = credentials.readConfigFile()
    args = getArgs()

    if len(sys.argv) == 1:
        runSync(credentials)
    else:
        if (not credentials_loaded and not args.credentials
            and not args.setup):
            print(
                """Credentials file not found. Please run 'ebay_sync -s'"""
                """ or 'ebay_sync -c' to create the credentials file."""
            )
            exit()
        else:
            run_setup(credentials, args)

if __name__ == '__main__':
    sys.exit(main())
