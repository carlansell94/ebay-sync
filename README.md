Simple application to pull seller information from your eBay account using the eBay API.

This is currently functional, but considered a pre-release version.

## Features
* Fetches orders, fees and feedback
* Able to pull in tracking numbers for labels purchased through eBay - though unfortunately, the API does not reliably return this info in all cases
* Support for multiple orders per tracking number
* Syncs partial/full refund information
* Includes fields to enter tracking and carrier info
* Works with the new eBay managed payments system
* Includes basic support for eBay digital signatures

## Notes
* The feedback sync currently fetches all feedback for a seller, updating records which already exist in the database. There is currently no link to the relevent sales record, due to eBay changing the format of legacy order IDs. A more long-term fix will be explored in a future update.
* Postage pricing must be added manually - even if the label is purchased through eBay.
* Fulfillment carrier name is based on the carrier chosen by the buyer. This will need to be updated manually should you use a different carrier.
* eBay fee refunds must be entered manually.

# Installation
You can install the current pre-release version of this app using pip.

```
pip install https://github.com/carlansell94/ebay-sync/releases/download/v0.6/ebay-sync.tar.gz
```

This is the recommended way to install this app, to ensure all dependencies are installed.

# Usage
This package is designed to be used as a module.

## Basic Usage
To run the sync, use the command

```
python3 -m ebay_sync
```

This can be used with a scheduler (such as cron) to periodically sync new data.

## Optional Parameters


| Flag           | Description |
| -------------- | ----------- |
| ```-c```       | Run the credentials setup |
| ```-i```       | Install the database schema |
| ```-s```       | Sets up the credentials, and installs the database schema. Equivalent to running -c and -i |
| ```-r "url"``` | Fetch a new API refresh token, using the provided auth URL |
| ```-a```       | Add a new API Auth'n'Auth token |
| ```-k```       | Generate a new digital signature signing key |
| ```-t```       | Test the database/API credentials |

## Initial Setup

Before the first sync, you'll need to run

```
python3 -m ebay_sync -s
```

to complete the application setup. This will configure your database and eBay API credentials.

# Generating a New Refresh Token
The eBay API requires a long-lived refresh token, which lasts for around 18 months. This token allows the shorter-lived oauth tokens to be generated as and when required.

Once this expires, the sync will fail to run. If you're seeing token errors, this is likely to be the issue.

To generate a new refresh token, complete the test sign-in on your eBay developer account.

Take the full response URL, which should look something like

```
https://signin.ebay.com/ws/eBayISAPI.dll?ThirdPartyAuthSucessFailure&isAuthSuccessful=true&code=v%5E1.1%23i%5E1%23p%5E3%23I%5E3%23f%5E0%23r%5E1%23t%5EUl41XzW5E8kLaWafjhuUGYIWR8yDQADuhDUWDN763tz&expires_in=299
```

Run the application, using the ```-r``` flag. Paste in your response URL as a parameter, enclosed in quotes.

```
python3 -m ebay_sync -r "https://signin.ebay.com/ws/eBayISAPI.dll?ThirdPartyAuthSucessFailure&isAuthSuccessful=true&code=v%5E1.1%23i%5E1%23p%5E3%23I%5E3%23f%5E0%23r%5E1%23t%5EUl41XzW5E8kLaWafjhuUGYIWR8yDQADuhDUWDN763tz&expires_in=299"
```

The application will fetch a new refresh token, and update your config with the new value.

The auth token in the response URL is only valid for 5 minutes, and is a one time code. If the refresh token does not update successfully, complete a new test sign-in to generate a new response URL.

# Digital Signatures
Ditigal signatures are required for certain API calls in the Finances, Fulfillment, Trading and Post-Order APIs. This app supports generating the required digital signature, as well as creating the appropriate headers to use for the API call.

On first run, a digital signature will automatically be created and stored. The private key will be saved to ```setup/digital_signature.key```. A new key can be created at any time, using ```ebay_sync -k```.

Digital signatures are used to fetch financial information, using the Finances API.

# eBay API Notes
This section lists a few notes/quirks I have encountered with the eBay API, mostly so I don't forget when coming back to the project at a later date.

* Fulfilment HREFs returned by the sell/fulfillment/v1/order getShippingFulfillment endpoint are not always functional, sometimes returning a 404 error (despite appearing correct). This app now uses the similar, but seemingly more reliable, getShippingFulfillments instead.
* If a tracking number is removed from an order, the returned HREF uses the tracking number '999', rather than being removed completely.
* If eBay CS refund a buyer from their side (i.e. seller also keeps their money), the payment API will still show a payment status of 'FULLY_REFUNDED'. However, no refund details will exist.
* finances/getTransactions supports filtering by transaction type, but is not currently open to all sellers. Could be used to automatically fetch postage label costs when it becomes available.
* Feedback API syncs all available records on every run, due to changes to the format of legacy order IDs. So far, I have been unable to use the OrderLineItemID field, and this value is not returned in the output. Hopefully, this is a quirk of the API which will be fixed in the future.

# Future Development
While the app is working (and runs daily on my machine), there are still a few enhancements planned before I would consider it to be 'stable'.

* Improved handling of API error responses.
* Increased logging of issues.
* Functions to retrieve data for output elsewhere.
* General tidy up, restructuring and PEP 8 conformance
