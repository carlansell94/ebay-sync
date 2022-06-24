#!/usr/bin/env python3

import MySQLdb
from subprocess import Popen, PIPE
from core.ebayapi import ebayAPI
from getpass import getpass

def installDb(db_name) -> bool:
    commands = [
        "mysql",                
        "--defaults-file=%s" % ('../core/credentials.ini',) , 
        "--database", db_name,
        "--unbuffered",
        "--execute", 'SOURCE ../setup/schema.sql'
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
        MySQLdb.connect(db=credentials['name'], user=credentials['user'],
                        passwd=credentials['password'])
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

    return True

def checkEbayAPICredentials(credentials: dict, oauth_token: str) -> bool:
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    if not ebayAPI.getAccessToken(scope, credentials, oauth_token):
        print("Error obtaining eBay API access token")
        return False

    return True
