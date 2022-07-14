#!/usr/bin/env python3

import MySQLdb
from getpass import getpass
from pathlib import Path
from subprocess import Popen, PIPE

from ..lib.api_request import APIrequest

def installDb(db_name) -> bool:
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

def checkDbIsEmpty(db) -> bool:
    query = db.cursor()
    query.execute("""SHOW TABLES""")
    
    if query.fetchone() is None:
        return True
    
    return False
