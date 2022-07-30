#!/usr/bin/env python3

import MySQLdb
from getpass import getpass
from pathlib import Path
from subprocess import Popen, PIPE

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

    process = Popen(commands, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 1:
        print(f"Error setting up database: {stderr}")
        return False

    return True

def getDbCredentials() -> dict:
    print("")
    print("--- DATABASE CREDENTIALS ---")
    print("----------------------------")

    credentials = {
        'name': input("Database name: "),
        'user': input("Username: "),
        'password': getpass("Password: ")
    }

    return credentials

def getEbayAPICredentials() -> dict:
    print("")
    print("--- EBAY API CREDENTIALS ---")
    print("----------------------------")

    credentials = {
        'app_id': input("App ID: "),
        'dev_id': input("Dev ID: "),
        'cert_id': input("Cert ID: "),
        'authnauth': input("Auth'n'auth token: "),
        'refresh_token': input("Refresh token: ")
    }

    return credentials

def checkDbCredentials(credentials: dict) -> bool:
    try:
        MySQLdb.connect(
            db=credentials['name'],
            user=credentials['user'],
            passwd=credentials['password']
        )
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

    return True

def checkEbayAPICredentials(refresh_token: str, oauth_token: str) -> bool:
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    if not APIrequest.getAccessToken(scope, refresh_token, oauth_token):
        print("Error obtaining eBay API access token")
        return False

    return True

def checkAllCredentials(credentials: dict) -> bool:
    valid = True

    if not checkDbCredentials(credentials):
        valid = False
    
    oauth_token = credentials.getOauthToken(
        credentials.ebay_app_id,
        credentials.ebay_cert_id
    )

    if not checkEbayAPICredentials(
        credentials.ebay_refresh_token,
        oauth_token
    ):
        valid = False
    
    return valid

def checkDbIsEmpty(db) -> bool:
    query = db.cursor()
    query.execute("""SHOW TABLES""")
    
    if query.fetchone() is None:
        return True
    
    return False

def installDb(db, db_name: str) -> bool:
    print("Installing database...")

    if not checkDbIsEmpty(db):
        confirm = input(
            """Database is not empty. Continuing will drop existing """
            """tables used by this app. Do you want to continue? (y/n): """
        )

        if confirm != 'Y' and confirm != 'y':
            return False

    return __import_schema(db_name)

def credentialsSetup(credentials):
    db_credentials = getDbCredentials()

    while not checkDbCredentials(db_credentials):
        db_credentials = getDbCredentials()

    ebay_credentials = getEbayAPICredentials()
    oauth_token = credentials.getOauthToken(
        ebay_credentials['app_id'],
        ebay_credentials['cert_id']
    )

    while not checkEbayAPICredentials(
        ebay_credentials['refresh_token'],
        oauth_token
    ):
        ebay_credentials = getEbayAPICredentials()

    config = {
        'client': db_credentials,
        'ebay': ebay_credentials
    }

    credentials.setConfig(config)
    credentials.saveConfigFile()

    print("")
    print("Credentials have been saved.")
