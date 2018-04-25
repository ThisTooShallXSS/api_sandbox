Author: ThisTooShallXSS

This script uses the JAMF API to poll system information from devices managed by Casper.
All request and parsing functions are wrapped in a class 'CasperConnection'. Objects are
returned from the main parsing functions which can be easily extended to include other
available device attributes.

To run:
- Simply call `python casper_query_api.py`
- The first run will have you set up the URL, and credentials.

Required Python libraries:
- pickle
- requests
