#!/usr/bin/env python3

from getpass import getpass
from pathlib import Path
from subprocess import Popen, PIPE
from urllib.parse import urlparse, parse_qs
import MySQLdb

from ..lib.api_request import APIrequest

def __import_schema(db_name) -> bool:
    path = str(Path(__file__).parent.absolute())

    credentials_path = path + "/credentials.ini"
    schema_path = path + "/schema.sql"

    commands = [
        "mysql",
        f"--defaults-file={credentials_path}",
        "--database", db_name,
        "--unbuffered",
        "--execute",
        f"SOURCE {schema_path}"
    ]

    with Popen(commands, stdout=PIPE, stderr=PIPE) as process:
        _, stderr = process.communicate()

        if process.returncode == 1:
            print(f"Error setting up database: {stderr}")
            return False

    return True

def get_db_credentials() -> dict:
    print("")
    print("--- DATABASE CREDENTIALS ---")
    print("----------------------------")

    credentials = {
        'name': input("Database name: "),
        'user': input("Username: "),
        'password': getpass("Password: ")
    }

    return credentials

def get_ebay_api_credentials() -> dict:
    print("")
    print("--- EBAY API CREDENTIALS ---")
    print("----------------------------")

    credentials = {
        'app_id': input("App ID: "),
        'dev_id': input("Dev ID: "),
        'cert_id': input("Cert ID: "),
        'authnauth': input("Auth'n'auth token: "),
        'refresh_token': input("Refresh token: "),
        'redirect_url': input("Redirect URL name: ")
    }

    return credentials

def check_db_credentials(credentials: dict) -> bool:
    try:
        MySQLdb.connect(
            db=credentials['name'],
            user=credentials['user'],
            passwd=credentials['password']
        )
    except Exception as error:
        print(f"[ERROR] Unable to connect to the database: {error}")
        return False

    return True

def check_ebay_api_credentials(refresh_token: str, oauth_token: str) -> bool:
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    if not APIrequest.get_access_token(scope, refresh_token, oauth_token):
        print("[ERROR] Unable to obtain eBay API access token")
        return False

    return True

def check_all_credentials(credentials: dict) -> bool:
    valid = True

    if not check_db_credentials(credentials):
        valid = False

    oauth_token = credentials.get_oauth_token(
        credentials.ebay_app_id,
        credentials.ebay_cert_id
    )

    if not check_ebay_api_credentials(
        credentials.ebay_refresh_token,
        oauth_token
    ):
        valid = False

    return valid

def check_db_is_empty(db) -> bool:
    query = db.cursor()
    query.execute("""SHOW TABLES""")

    if query.fetchone() is None:
        return True

    return False

def install_db(db, db_name: str) -> bool:
    print("[INFO] Installing database...")

    if not check_db_is_empty(db):
        confirm = input(
            """Database is not empty. Continuing will drop existing """
            """tables used by this app. Do you want to continue? (y/n): """
        ).upper()

        if confirm != 'Y':
            return False

    return __import_schema(db_name)

def credentials_setup(credentials):
    db_credentials = get_db_credentials()

    while not check_db_credentials(db_credentials):
        db_credentials = get_db_credentials()

    ebay_credentials = get_ebay_api_credentials()
    oauth_token = credentials.get_oauth_token(
        ebay_credentials['app_id'],
        ebay_credentials['cert_id']
    )

    while not check_ebay_api_credentials(
        ebay_credentials['refresh_token'],
        oauth_token
    ):
        ebay_credentials = get_ebay_api_credentials()

    config = {
        'client': db_credentials,
        'ebay': ebay_credentials
    }

    credentials.set_config(config)
    get_new_signing_key(ebay_credentials['refresh_token'], oauth_token)
    credentials.save_config_file()

    print("")
    print("[INFO] Credentials have been saved.")

def get_new_refresh_token(url: str, oauth_token: str, runame: str):
    url = urlparse(url)

    try:
        auth_code = parse_qs(url.query)['code'][0]
    except KeyError as _:
        print(
            """[ERROR] Auth code not found, ensure the full eBay auth URL """
            """is provided."""
        )
        return False

    return APIrequest.get_refresh_token(auth_code, oauth_token, runame)

def get_new_authnauth_token() -> str:
    return input("New Auth'n'auth token: ")

def get_new_signing_key(refresh_token: str, oauth_token: str):
    if access_token := APIrequest.get_access_token(
        'https://api.ebay.com/oauth/api_scope',
        refresh_token,
        oauth_token
    ):
        return APIrequest.get_signing_key(access_token)

    return False
