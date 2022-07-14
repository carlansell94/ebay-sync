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
        help="Update the stored refresh token with the provided value")
    parser_setup.add_argument("-t", "--test", action='store_true',
        help="Test the database/api credentials")

    return parser.parse_args()

def run_setup(credentials, args):
    if args.credentials:
        credentialsSetup(credentials)
        exit()

    if args.install:
        db = getDbConnection(credentials)

        if not db:
            print(
                """Please run 'ebay_sync -s' or 'ebay_sync -c to """
                """create a new credentials file."""
            )
            exit()
        
        if not schemaSetup(db, credentials.client_name):
            print(
                """Unable to install database, check the specified user """
                """has the required privileges. Alternatively, load the """
                """included schema.sql file into your database."""
            )
        else:
            print("Database installed successfully.")

        exit()

    if args.test:
        if validCredentials(credentials):
            print("Test completed successfully, credentials are valid.")
        else:
            print(
                """Errors found, please run ebay_sync -s or ebay_sync -c """
                """to create a new credentials file."""
            )
        exit()

    if args.refresh_token is not None:
        credentials.updateRefreshToken(args.refresh_token)

        if checkEbayAPICredentials(credentials):
            credentials.saveConfigFile()
            print("Updated token has been saved.")
        else:
            print(
                """Updated token is not valid, the previous token has """
                """been retained."""
            )
            
        exit()

def credentialsSetup(credentials):
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

def schemaSetup(db, db_name: str):
    print("Installing database...")

    if not setup.checkDbIsEmpty(db):
        confirm = input(
            """Database is not empty. Continuing will drop existing """
            """tables used by this app. Do you want to continue? (y/n): """
        )

        if confirm != 'Y' and confirm != 'y':
            print("Exiting...")
            exit()

    return setup.installDb(db_name)

def validCredentials(credentials) -> bool:
    valid = True
    
    if not checkDatabaseCredentials():
        print("Invalid database credentials.")
        valid = False
            
    if not checkEbayAPICredentials(credentials):
        print("Invalid eBay API credentials.")
        valid = False
            
    return valid

def checkDatabaseCredentials() -> bool:
    return setup.checkDbCredentials()

def checkEbayAPICredentials(credentials) -> bool:
    oauth_token = credentials.getOauthToken(
        credentials.ebay_app_id,
        credentials.ebay_cert_id
    )

    if setup.checkEbayAPICredentials(
        credentials.ebay_refresh_token,
        oauth_token
    ):
        return True
    
    return False

def runSync(credentials):
    db = getDbConnection()

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
