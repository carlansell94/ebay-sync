Simple application to pull seller information from your ebay account using the ebay API.
  
Features:
* Fetches orders, fees and feedback
* Includes fields to enter tracking info, actual postage cost and carrier info (currently must be done manually)
  
Requirements:
* Python 3
* MySQLdb
* eBay developer account
  
How To Use:
* Create a database using the schema file in /setup.
* Fill in the credentials.ini file.
* Move credentials.ini to /core.
* Run sync/run.py to start.
  
eBay Credentials:
In order to use this application, you will need to sign up for an eBay developer account, and create a production app.  

You will also need to add your Auth'n'Auth token, and OAuth refresh token. This app is currently unable to generate refresh tokens from authorisation codes.
