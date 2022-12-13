""" --------------------------------------------------------------------------------------------------------------------
PyTenable - Revision Count Writer:
    This script will write the number of Code Revisions available for a PLC as a custom field. 
    Create the custom field called "Revisions" in Tenable.ot before running the script.
    A new code revision will occur after a snapshot reveals a change in ladder logic or PLC tags.
    Code Snapshots are not enabled by default, and may need to be turned on for this script to work.

  Before you can run this, you must generate a Tenable.ot API Key that can be used for authentication. 
  You can generate the key under Local Settings -> System Configuration ->  'API Keys' if necessary.

  To install pyTenable:
      pip install pytenable
# ------------------------------------------------------------------------------------------------------------------ """

import logging
logging.basicConfig(level=logging.ERROR)

""" --------------------------------------------------------------------------------------------------------------------
#  Edit the variables here to point to your address of TOT, as well as your API key. 
# ------------------------------------------------------------------------------------------------------------------ """
from tenable.ot import TenableOT            # It is necessary to import pyTenable library for connecting to Tenable.ot

api_key = 'REPLACE_THIS_WITH_YOUR_API_KEY'  # This is the API key that you generate within Tenable.ot
url = 'https://192.168.1.5'                 # This is the IP or FQDN of your instance of Tenable.ot

tot = TenableOT(api_key=api_key, url=url)   # This builds the connection to Tenable.ot for the rest of this pyTenable script to use.

""" --------------------------------------------------------------------------------------------------------------------
#  This func finds the customField UUID associated with "Revisions", and then writes "rev_assets" to that field. Returns the count of total assets updated.
# ------------------------------------------------------------------------------------------------------------------ """
def updateAssetRevisions(tags, rev_assets):
    
    counter = 0                                         # Set the counter to 0 so we can know after the for loop how many assets were edited.
                                     
    for y in range(len(tags)):                          # Find customField## tied to "Revisions" by looping over all tags.
        if "Revisions" in tags[y]["userDefinedName"]:   # If we see the name "Revisions" present for one of the custom fields.
            #print("Found Field: ", tags[y]["fieldId"], "Name: ", tags[y]["userDefinedName"])
            revisions_field_uuid = tags[y]["fieldId"]   # We've found the field ID, and are assigning it to a var.

    for x in range(len(rev_assets)):                    # For loop over each asset with revision data in the array.
        asset_id = rev_assets[x]['id']                  # Save each asset ID with revisions so we can later update that asset.
        count_to_save = str(rev_assets[x]['count'])     # Determine how many revisions are present. 
        asset_name = rev_assets[x]['name']              # Save the asset's name to a var for logging purposes. 

        resp = tot.graphql(                             # tot.graphql() is our built-in pytenable handler for interactions with Tenable.ot via graphQL.
            operationName='updateAsset',                # Maps to the kind of GraphIQL Query you're making. Others include getIemAssets, getAsset, getEvents
            variables={
              'customFields' : {revisions_field_uuid : count_to_save}, # Uses the field UUID and the number of code revisions.
              'id' : asset_id                           # This is the asset UUID for the PLC or controller with code revisions.
            },                                          # This next line is the GraphQL query we use to update a custom field.
            query='''                                   
                    mutation updateAsset($id: ID!, $name: String, $customFields: CustomFieldValue){
                
                      updateAsset(id: $id, name: $name, customFields: $customFields) {
                        id
                        name
                      }
                    }
                  ''')

        if resp:                                        # If we receive a successful response, we know the tag was written.
            print("(WRITING) Revision Count: ", count_to_save, "   Name: ", asset_name) # Output in shell the count and name of all updated revision counts.
            counter += 1                                # Increment the counter since we successfully wrote the tag value to the asset.
        else:
          print("(ERROR) Unable to write Revision tag to asset: ", asset_name)
          break                                         # Bail at the first failed tag write to save time. Something is wrong
    
    return counter     

""" --------------------------------------------------------------------------------------------------------------------
#  This func iterates over each applicable PLC/Controller and checks to see how many revisions it has, and returns an integer.
# ------------------------------------------------------------------------------------------------------------------ """
def get_revision_count(asset_id):

    #from pprint import pprint                          # If we're not using pprint(), we can comment this out. If you want to use pprint() below you will need to uncomment this.
    resp = tot.graphql(                                 # tot.graphql() is our built-in pytenable handler for interactions with Tenable.ot via graphQL.
        operationName='getAssetDetails',                # Maps to the kind of GraphIQL Query you're making. Others include getIemAssets, getAsset, getEvents
        variables={
                  'asset' : asset_id                    # Since we're asking for a single asset's details, we need to pass the ID.
                  },
        query='''
                query getAssetDetails($asset: ID!) {
                  asset(id: $asset) {
                  id
                  name
                  revisions {
                    nodes {
                      id
                      }
                    }
                  }
                }
              ''')
                                                        # The graphQL query can be shortened to speed it up.
                                                        # In this case, we're only looking for revisions per asset.
    #pprint(resp)                                       # Adding pprint() in these graphQL queries is useful to see the entire response neatly formatted.
    revisions = resp['data']['asset']['revisions']['nodes'] # Assign the response data from GraphQL, and point to the field we need.

    return len(revisions) # Calculate and return an integer for however many code revisions are present for that asset.
      
""" --------------------------------------------------------------------------------------------------------------------
#  This checks an individual asset ID to determine whether or not snapshots/code revisions are supported for that device. Returns True/False.
# ------------------------------------------------------------------------------------------------------------------ """
def check_snapshot_supported(asset_id):

    resp = tot.graphql(                                 # tot.graphql() is our built-in pytenable handler for interactions with Tenable.ot via graphQL.
        operationName='getAssetSupported',              # Maps to the kind of GraphIQL Query you're making. Others include getIemAssets, getAsset, getEvents
        variables={
                  'asset' : asset_id                    # Since we're asking for a single asset's capabilities, we need to pass the ID.
                  },
        query='''
                query getAssetSupported($asset: ID!) {
                  asset(id: $asset) {
                  id
                  canSnapshot { supported }
                  } }
              ''')
    
    # Example response data for an asset that CAN do snapshots.
    # {'data': {'asset': {'id': 'ffd91fd2-950d-403d-a6b4-dfb26ac46de9', 'canSnapshot': {'supported': True}}}}

    snapshot_feasibility = resp['data']['asset']['canSnapshot']['supported'] # Assign the response data from GraphQL, and point to the field we need.

    return snapshot_feasibility

""" --------------------------------------------------------------------------------------------------------------------
#  This checks an individual asset ID to count how many snapshots/code revisions are present, and returns an array of asset ID+revision count data.
# ------------------------------------------------------------------------------------------------------------------ """
def get_revisions():

    all_controllers = get_controllers()                 # Uses the built-in assets.list() function in pytenable to grab all relevant devices.
    rev_assets = []                                     # Create an empty array.

    for asset in all_controllers:                       # For loop over all controllers found in the assets.list() filtered query.
        rev_pair = {}                                   # Create the dict for storing each id+rev_count+name combo.
        asset_name = asset.details["name"]                         # You can reference vars() of the asset object directly using ".name" for example.

        if check_snapshot_supported(asset.id):          # If this is a controller or PLC that we support code revision snapshots for.
            rev_count = get_revision_count(asset.id)    # Determine how many code revisions there are for that specific asset.
            print("(READING) Found Rev Count: ", rev_count, "    Name: ", asset_name)
            # This is a useful debug statement when fetching the code revisions count from each controller. It gives you feedback that the script is working.

            rev_pair['id'] = asset.details["id"]
            rev_pair['count'] = rev_count
            rev_pair['name'] = asset_name
            rev_assets.append(rev_pair)                 # Append this asset's dict of 3 data points to the end of the array.

    return rev_assets                                   # Return a large dict of all controllers with revisions. Includes their count, name, ID.


""" --------------------------------------------------------------------------------------------------------------------
#  This area is used to fetch all of the user-defined custom fields, and returns json of information for each tag+id.
# ------------------------------------------------------------------------------------------------------------------ """
def get_custom_fields():

    resp = tot.graphql(
    operationName='getCustomFields',                    # Maps to the kind of GraphIQL Query you're making. Others include getIemAssets, getAsset, getEvents
    query = "query getCustomFields { customFields { fieldId userDefinedName }}"   # Very short graphQL query to get any user-defined custom fields. 
    )

    custom_fields = resp["data"]['customFields']                 # Point to the custom field data (ids and names), and return that info to the parent func.

    return custom_fields
""" --------------------------------------------------------------------------------------------------------------------
#  This will fetch only relevant PLC/Controller assets using the built-in pyTenable function. Returns an object for each asset, usable in for-loop.
# ------------------------------------------------------------------------------------------------------------------ """
def get_controllers():

    filter_controllers={"op":"And",                     # This is our filter statement, to limit what we get back from assets.list()
                      "expressions":[
                      {"field":"type","op":"In","values":['Plc', 'Cp', 'PowerSupply', 'Controller', 'Rtu', 'Dcs']}, # Filter down to the device types that have snapshots.
                      {"field":"hidden","op":"Equal","values":"false"} # Need to prevent this from pulling in hidden assets and controllers.
                      ]}
      
    return tot.assets.list(filter=filter_controllers) # assets.list() is a pyTenable built-in function for querying all Tenable.ot assets via graphQL.

""" --------------------------------------------------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------------------------------------------------ """
def main():

  updated_count = 0                                     # Set this to zero, so we know if there were any controllers found with even a single code revision.
  custom_fields = get_custom_fields()                   # This is the function that grabs our data for all custom fields.
  assets_with_revisions = get_revisions()               # This is the main workhorse of the script. This func pulls in all the data.
  updated_count = updateAssetRevisions(custom_fields, assets_with_revisions) # Once we've pulled in all controller revision data, this writes the count to the custom field.

  if updated_count != 0:
    print("\n(SUCCESS) The script has completed. The custom field for Revisions has been updated for each relevant asset.\n")
    print("(SUCCESS) Total Assets updated with Code Revisions tag: ", updated_count, '\n')
  else:
    print('\n(ERROR) No assets were found to have code revisions. Check that "Code Snapshots" feature is enabled within Tenable.ot.\n')
if __name__ == '__main__':
    main()
