""" --------------------------------------------------------------------------------------------------------------------
Python Tenable.ot - Advanced Single Asset Pull:

Before you can run this, you must generate an API Key that can be used for authentication. 
You can generate the key under Local Settings -> System Configuration ->  'API Keys' if necessary.

To run this script:
   $ python3 py-request-ot-asset-info.py

You can also directly pass in the UUID:
   $ python3 py-request-ot-asset-info.py <asset_uuid_here>
   $ python3 py-request-ot-asset-info.py 4db49aa5-90c4-4820-a511-750d66715d42

# ------------------------------------------------------------------------------------------------------------------ """

import requests
import json
import pickle
import os
import sys

requests.packages.urllib3.disable_warnings()

""" --------------------------------------------------------------------------------------------------------------------
This takes in the user input, and saves their Tenable.ot location and API key. Saves as 'keys.pickle' in the same dir.
# ------------------------------------------------------------------------------------------------------------------ """

def save_keys():
    #assumption is that the user keys didn't work or don't exist
    print("Hey you don't have any Keys or TOT Server stored!")
    
    tenable_ot_url = input("Please provide your Tenable.ot IP address or FQDN : ")
    api_key = input("Please provide your API Key : ")

    dicts = {"Tenable OT URL":tenable_ot_url, "API Key": api_key}

    pickle_out = open("keys.pickle", "wb")
    pickle.dump(dicts, pickle_out)
    pickle_out.close()

    print("Now you have keys, re-run your command")
    sys.exit()


""" --------------------------------------------------------------------------------------------------------------------
This builds the request headers from saved token and URL information. Used by the GET and POST functions below.
# ------------------------------------------------------------------------------------------------------------------ """

def grab_headers():
    api_key = ''
    tenable_ot_url = ''

    #check for API keys; if none, get them from the user by calling save_keys()
    if os.path.isfile('./keys.pickle') is False:
        save_keys()
    else:
        pickle_in = open("keys.pickle", "rb")
        keys = pickle.load(pickle_in)
        tenable_ot_url = keys["Tenable OT URL"]
        api_key = keys["API Key"]

    #set the header
    headers = {'Content-type':'application/json','X-ApiKeys':'key=' + api_key}
    return headers, tenable_ot_url

def get_data(url_mod, payload):
    '''
    :param url_mod: The URL endpoint. Ex: /scans
    :return: Response from API in json format
    '''
    tenable_ot_url = grab_headers()[1]
    url = "https://" + tenable_ot_url + ":443"
    headers = grab_headers()[0]
    r = requests.request('GET', url + url_mod, json=payload, headers=headers, verify=False)
    data = r.json()
    return data

def post_data(url_mod, payload):
    '''
    :param url_mod: The URL endpoint. Ex: /scans/<scan-id>/launch
    :return: Response from the API
    '''
    tenable_ot_url = grab_headers()[1]
    url = "https://" + tenable_ot_url + ":443"
    headers = grab_headers()[0]
    r = requests.post(url + url_mod, json=payload, headers=headers, verify=False)
    return r

""" --------------------------------------------------------------------------------------------------------------------
This uses a short and simple GraphQL query for "details" about the asset UUID passed to this function. This outputs
each data point that Tenable.ot knows about that asset.
# ------------------------------------------------------------------------------------------------------------------ """

def fetch_asset_details(asset_uuid):
  url_modified_graphql = '/graphql'

  payload = {"query" : "query getAsset($asset: ID!){asset(id:$asset){details}}", "variables" : {"asset":asset_uuid}}
  #print(payload)
  asset_details = post_data(url_modified_graphql, payload)

  # Example asset
  # Asset Details:  {'id': 'fe3ebf15-2aae-42d7-a3c3-1757f76124e4', 'name': 'Heat_Rollers_4', 'firstSeen': '2021-10-29T19:23:05.229557Z', 'lastSeen': 
'2022-08-29T20:15:42.254035Z', 
                     """
                    'macs': ['00:1d:9c:db:d9:6b', '00:1d:9c:db:29:14'], 'ips': ['172.27.52.53', '172.27.52.52'], 'type': 'Plc', 'superType': 
'Controller', 'category': 'ControllersCategory', 'purdueLevel': 'Level1', 
                    'vendor': 'Rockwell', 'runStatus': 'Stopped', 'runStatusTime': '2022-08-29T20:07:51.60205Z', 'rawFamily': 'ControlLogix5570', 
'family': 'ControlLogix 5570', 'modelName': '1756-L71/B LOGIX5571', 
                    'firmwareVersion': '30.011', 'serial': '######', 'slot': 0, 'backplane': 'faf1b856-f022-4150-bfdf-b5b937118dab', 'backplaneName': 
'Backplane #1', 'risk': 71.66493544169893, 'criticality': 'HighCriticality', 
                    'hidden': False, 'lastUpdate': '2022-08-29T20:16:00.428292Z', 'customField1': "Smyrna", 'cip': {'deviceType': 'PLC'}, 
'classificationIncidents': ['CipIdentityPlcIncident', 'IcsActivityDstPlcIncident', 'BackplaneIncident', 
                    'ConversationIcsProtocolDstIncident'], 'common': {'plcName': 'Heat_Rollers_4', 'keyState': 'Remote'}, 'names': [{'id': 
'fe3ebf15-2aae-42d7-a3c3-1757f76124e4', 'source': 'Default', 'value': 'PLC #3'}, 
                    {'id': 'fe3ebf15-2aae-42d7-a3c3-1757f76124e4', 'source': 'Project', 'value': 'Heat_Rollers_4'}, {'id': 
'fe3ebf15-2aae-42d7-a3c3-1757f76124e4', 'source': 'Chosen', 'value': 'Heat_Rollers_4'}], 
                    'customFields': [['customField1', 'Asset Owner/Team', 'PlainText']], 'directIp': None, 'directIps': None, 'directMac': None, 
'directMacs': None, 'additionalIp': None, 'additionalIps': ['172.27.52.53', '172.27.52.52'], 
                    'additionalMac': None, 'additionalMacs': ['00:1d:9c:db:d9:6b', '00:1d:9c:db:29:14'], 'stateUpdateTime': 
'2022-08-29T20:07:51.60205Z', 'extendedSegments': [{'id': '6add2a3c-28b7-4325-96b0-fc1174e4f50c', 
                    'name': 'Controller / 172.27.52.X', 'archived': False, 'system': True, 'key': 'AG1-3', 'type': 'Segment', 'systemName': 'Controller 
/ 172.27.52.X', 'vlan': None, 'description': None, 
                    'isPredefinedName': True, 'subnet': '172.27.52.X', 'assetType': 'Controller'}], 'state': 'Stopped'} 
                     """
  return asset_details.text

""" --------------------------------------------------------------------------------------------------------------------
This polls a less commonly used API endpoint to find out information on the performance of queries or identification.
# ------------------------------------------------------------------------------------------------------------------ """

def fetch_asset_stats(asset_uuid):

  url_modified_stats = "/v1/activeclients/" + asset_uuid + "/stats"

  stats_response = get_data(url_modified_stats, None)
  stats = stats_response["Stats"]
  
  return stats

""" --------------------------------------------------------------------------------------------------------------------
Our main entry point. We get the UUID and pass it over to the two fetch jobs. Then we print to stdout for this example.
# ------------------------------------------------------------------------------------------------------------------ """

def main():

    try:
        asset_uuid = sys.argv[1]

    except:
        asset_uuid = input("Please provide a Tenable.ot asset UUID : ")

    if len(asset_uuid) != 36:
        print("This is an invalid asset UUID!")
        sys.exit()

    try:
        asset_data = json.loads(fetch_asset_details(asset_uuid))["data"]["asset"]["details"]
        asset_stats = fetch_asset_stats(asset_uuid)
    except:
        print("Something went wrong when pulling the information from Tenable.ot.")
        print("Consider deleting keys.pickle (in this folder) and then re-run the script.")
        sys.exit()
 
    print("\n\nThis data comes from the graphql endpoint to ask for the details for: ", asset_uuid, '\n')
    print("Asset Details: \n")

    for key, value in asset_data.items():
        print(key, ": ", value)

    print("\nThis data comes from the OT /v1 endpoint to ask for the query stats for: ", asset_uuid)

    for key, value in asset_stats.items():
      print('\n', "Query Type: ", key)
      for x in value:
        print('\t', x, ': ', value[x])

if __name__ == '__main__':
    main()
