""" --------------------------------------------------------------------------------------------------------------------
PyTenable - Basic Asset Pull:

Before you can run this, you must generate an API Key that can be used for authentication. 
You can generate the key under Local Settings -> System Configuration ->  'API Keys' if necessary.

To install pyTenable:
    pip3 install pytenable 
# ------------------------------------------------------------------------------------------------------------------ """

from tenable.ot import TenableOT

""" --------------------------------------------------------------------------------------------------------------------
#  Edit the variables here to point to your address of TOT, as well as your API key. 
# ------------------------------------------------------------------------------------------------------------------ """

tot = TenableOT(api_key='REPLACE_THIS_WITH_YOUR_API_KEY', url='https://192.168.1.5')

for asset in tot.assets.list():
    pprint(vars(asset))
    print('\n')