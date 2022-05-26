""" --------------------------------------------------------------------------------------------------------------------
PyTenable - Advanced Asset Pull:

Before you can run this, you must generate an API Key that can be used for authentication. 
You can generate the key under Local Settings -> System Configuration ->  'API Keys' if necessary.

To install pyTenable:
    pip3 install pytenable 
# ------------------------------------------------------------------------------------------------------------------ """

import logging
logging.basicConfig(level=logging.ERROR)

""" --------------------------------------------------------------------------------------------------------------------
#  Edit the variables here to point to your address of TOT, as well as your API key. 
# ------------------------------------------------------------------------------------------------------------------ """
from tenable.ot import TenableOT
api_key = 'REPLACE_THIS_WITH_YOUR_API_KEY'  # This is the API key that you generate within Tenable.ot
url = 'https://192.168.1.5'                 # This is the IP or FQDN of your instance of Tenable.ot

tot = TenableOT(api_key=api_key, url=url)

""" --------------------------------------------------------------------------------------------------------------------
#  This will fetch every T.ot asset, without any filters. Returns an object for each asset that you can for-loop over.
# ------------------------------------------------------------------------------------------------------------------ """
def get_all_assets():

    return tot.assets.list()

""" --------------------------------------------------------------------------------------------------------------------
#  This will fetch only assets in "Controllers & Modules" view. Returns an object for each asset, usable in for-loop.
# ------------------------------------------------------------------------------------------------------------------ """
def get_controllers(search_string):

    filter_controllers = {"op":"And",
                      "expressions":[
                      {"field":"category","op":"In","values":['ControllersCategory']},
                      {"field":"hidden","op":"Equal","values":"false"}
                      ]}
   
# The filter below this line is another example of how to find specific device types.
#  filter_controllers={"op":"And",
#                      "expressions":[
#                      {"field":"type","op":"In","values":['Plc', 'Cp', 'PowerSupply', 'Controller', 'Rtu', 'Dcs']},
#                      {"field":"hidden","op":"Equal","values":"false"}
#                      ]}

    return tot.assets.list(filter=filter_controllers, search=search_string)

""" --------------------------------------------------------------------------------------------------------------------
#  This will fetch only assets in "Network Devices" view. Returns an object for each asset, usable in for-loop.
# ------------------------------------------------------------------------------------------------------------------ """
def get_network_devices(search_string):

    filter_controllers={"op":"And",
                      "expressions":[
                      {"field":"category","op":"In","values":['NetworkAssetsCategory']},
                      {"field":"hidden","op":"Equal","values":"false"}
                      ]}
      
    return tot.assets.list(filter=filter_controllers, search=search_string)

""" --------------------------------------------------------------------------------------------------------------------
#  This will fetch only assets in "Network Devices" view. Returns an object for each asset, usable in for-loop.
# ------------------------------------------------------------------------------------------------------------------ """
def get_iot_devices():

    filter_controllers={"op":"And",
                      "expressions":[
                      {"field":"category","op":"In","values":['IotCategory']},
                      {"field":"hidden","op":"Equal","values":"false"}
                      ]}
      
    return tot.assets.list(filter=filter_controllers)

""" --------------------------------------------------------------------------------------------------------------------
# This basic function will count however many assets are returned by the GraphQL query.
# ------------------------------------------------------------------------------------------------------------------ """
def countAssets(data):
    counter = 0

    for asset in data:       # By this time, we're already working with a large dict() of Asset objects.
        counter += 1         # Increment the counter for each asset we see in the returned asset data from GraphQL.

    return counter

""" --------------------------------------------------------------------------------------------------------------------
# This basic function will print out all assets that are returned by the GraphQL query in a nice, readable format.
# ------------------------------------------------------------------------------------------------------------------ """
def printAssets(asset_data):
    from pprint import pprint

    for asset in asset_data:
        pprint(vars(asset))  # We're iterating over the assets, and printing out vars() because "Asset" is an object w/ attributes.
        print()              # Print an empty line between each asset, for easier readability.

    return

""" --------------------------------------------------------------------------------------------------------------------
# Main Execution - Customize this function to fit your needs. It relies on the functions above.
# ------------------------------------------------------------------------------------------------------------------ """
def main():

    empty_search_str = ''

    Assets_AllAssets = get_all_assets()
    Assets_Controllers = get_controllers(empty_search_str)
    Assets_RockwellControllers = get_controllers(search_string="Rockwell")
    Assets_NetworkDevices = get_network_devices(empty_search_str)
    Assets_Windows10Devices = get_network_devices(search_string="Windows 10")
    Assets_IoTDevices = get_iot_devices()

    print("Number of All Assets: ", countAssets(Assets_AllAssets))
    print("Number of All Controllers: ", countAssets(Assets_Controllers))
    print("Number of All Rockwell Controllers: ", countAssets(Assets_RockwellControllers))
    print("Number of All Network Devices: ", countAssets(Assets_NetworkDevices))
    print("Number of All Windows 10 Devices: ", countAssets(Assets_Windows10Devices))
    print("Number of All IoT Devices: ", countAssets(Assets_IoTDevices))

    print("All IoT Devices: \n")
    printAssets(Assets_IoTDevices)
    
    return

if __name__ == '__main__':
    main()
