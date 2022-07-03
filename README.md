Simple application to pull seller information from your eBay account using the eBay API.

## Features:
* Fetches orders, fees and feedback
* Able to pull in tracking numbers for labels purchased through eBay - though unfortunately, the API does not reliably return this info in all cases
* Support for multiple orders per tracking number
* Syncs partial/full refund information - though at present, eBay fee refunds need to be added manually
* Includes fields to enter tracking info, actual postage cost and carrier info (currently must be done manually)
* Works with the new eBay managed payments system

# Requirements:
* Python 3
* MySQLdb
* eBay developer account

In order to use this application, you will need to sign up for an eBay developer account, and create a production app. 

You will also need to add your Auth'n'Auth token, and OAuth refresh token. This app is currently unable to generate refresh tokens from authorisation codes.

# Installation
You can install the latest release of this app using pip.

```
pip install https://github.com/carlansell94/ebay-sync/releases/latest/ebay-sync.tar.gz
```

This is the recommended way to install this app, to ensure all dependencies are installed.

## Usage:
This app is packaged as a python module, and can be ran using

```
python3 -m ebay_sync
```

On first run, the app will ask for your database and eBay API credentials. If the provided database user has the required permissions, the database schema will be installed automatically. If not, you can set this up yourself using setup/schema.sql.

Once setup is complete, the app can be ran automatically using cron/systemd timers etc.

To re-run setup, delete setup/credentials.ini and re-run the app.
# eBay API Notes
This section lists a few notes/quirks I have encountered with the eBay API, mostly so I don't forget when coming back to the project at a later date.

* Fulfilment HREFs returned by the sell/fulfillment/v1/order endpoint are not always functional, sometimes returning a 404 error (despite appearing correct).
* If a tracking number is removed from an order, the returned HREF uses the tracking number '999', rather than being removed completely.
* If eBay CS refund a buyer from their side (i.e. seller also keeps their money), the payment API will still show a payment status of 'FULLY_REFUNDED'. However, no refund details will exist.
* finances/getTransactions supports filtering by transaction type, but is not currently open to all sellers. Could be used to automatically fetch postage label costs when it becomes available.

# Future Development:
While the app is working (and runs daily on my machine), there are still a few enhancements planned before I would consider it to be 'stable'.

* Improved handling of API error responses.
* Increased logging of issues.
* Addition of runtime flags to manage schema/credentials etc.
* Functions to retrieve data for output elsewhere.
* General tidy up, PEP 8 conformance
