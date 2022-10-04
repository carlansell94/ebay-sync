#!/usr/bin/env python3

import MySQLdb
import sys
import re
import argparse

from .get_feedback import GetFeedback
from .get_fulfillment import GetFulfillment
from .get_sales import GetSales
from .lib.sale import Sale
from .setup import setup
from .setup.credentials import Credentials

def get_args():
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
    parser_setup.add_argument("-a", "--authnauth-token",
        help="Set a new authnauth token", action='store_true')
    parser_setup.add_argument("-t", "--test", action='store_true',
        help="Test the database/api credentials")

    return parser.parse_args()

def run_setup(credentials, args):
    if args.credentials:
        setup.credentials_setup(credentials)
        sys.exit()

    if args.install:
        db = get_db_connection(credentials)

        if not db:
            print(
                """[ERROR] Please run 'ebay_sync -s' or 'ebay_sync -c to """
                """create a new credentials file."""
            )
            sys.exit()
        
        if not setup.install_db(db, credentials.client_name):
            print(
                """[ERROR] Unable to install database, check the specified """
                """user has the required privileges. Alternatively, """
                """load the included schema.sql file into your database."""
            )
        else:
            print("[INFO] Database installed successfully.")

        sys.exit()

    if args.test:
        if setup.check_all_credentials(credentials):
            print(
                """[INFO] Test completed successfully, credentials are """
                """valid."""
            )
        else:
            print(
                """[ERROR] Errors found, please run ebay_sync -s or """
                """ebay_sync -c to create a new credentials file."""
            )
        sys.exit()

    if args.refresh_token is not None:
        oauth_token = credentials.get_oauth_token(
            credentials.ebay_app_id,
            credentials.ebay_cert_id
        )

        new_refresh_token = setup.get_new_refresh_token(
            args.refresh_token,
            oauth_token,
            credentials.ebay_redirect_url
        )

        if new_refresh_token:
            credentials.set_option_value(
                'ebay_refresh_token',
                new_refresh_token
            )
            credentials.save_config_file()

            print(
                """[INFO] eBay API refresh token has been updated """
                """successfully."""
            )
        else:
            print(
                """[ERROR] Unable to fetch a new refresh token, check the """
                """provided return URL is valid."""
            )

        sys.exit()

    if args.authnauth_token:
        credentials.set_option_value(
            'ebay_authnauth',
            setup.get_new_authnauth_token()
        )
        credentials.save_config_file()
        sys.exit()

def run_sync(credentials):
    db = get_db_connection(credentials)

    sales = GetSales(db, credentials)
    if sales := sales.fetch():
        sales.parse()
    else:
        print("[ERROR] Failed to fetch sales data")

    fulfillment = GetFulfillment(db, credentials)
    for order_id in Sale.get_order_ids(db, days=90):    # 90 day API limit
        if fulfillment.fetch(order_id[0]):
            fulfillment.parse()
        else:
            print("""[ERROR] Failed to fetch fulfillment data for """
                  f"""order {order_id[0]}""")

    legacy_order_ids = Sale.get_order_ids(db, days=60, legacy_ids=True)
    for order_id in legacy_order_ids:
        if (re.match(r'[0-9]{12}-[0-9]{13}', str(order_id[0]))):
            if not GetFeedback(db, credentials).fetch(order_id[0]):
                break

def get_db_connection(credentials):
    try:
        db = MySQLdb.connect(
            db=credentials.client_name,
            user=credentials.client_user,
            passwd=credentials.client_password
        )
    except Exception as e:
        print(f"[ERROR] Unable to connect to the database: {e}")
        return False

    return db

def main():
    credentials = Credentials()
    credentials_loaded = credentials.read_config_file()
    args = get_args()

    if len(sys.argv) == 1:
        run_sync(credentials)
    else:
        if (not credentials_loaded and not args.credentials
            and not args.setup):
            print(
                """[ERROR] Credentials file not found. Please run """
                """'ebay_sync -s' or 'ebay_sync -c' to create the """
                """credentials file."""
            )
            sys.exit()
        else:
            run_setup(credentials, args)

if __name__ == '__main__':
    sys.exit(main())
