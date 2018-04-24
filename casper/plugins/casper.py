import os, sys, pickle
import json, requests

class mdm_host(object): # Object for storing device details.
    def __init__(self, name, serial_number, last_reported_ip,
                 mac_address, model, model_identifier,
                 os_name, os_version, os_build):
        self.name = name
        self.serial_number = serial_number
        self.last_reported_ip = last_reported_ip
        self.mac_address = mac_address
        self.model = model
        self.model_identifier = model_identifier
        self.os_name = os_name
        self.os_version = os_version
        self.os_build = os_build

class network_obj(object): # Object for storing managed networks.
    def __init__(self, _id, name, start_ip, end_ip):
        self._id = _id
        self.name = name
        self.start_ip = start_ip
        self.end_ip = end_ip

class CasperConnection:
    """
    This class handles all jobs which pull/parse data from Casper/JAMF.
    """
    # initialize connection vars
    casper_system_url = None
    casper_username = None
    casper_password = None

    def __init__(self):
        """
        Initializes Casper communication wrapper with saved pickle file. Calls save_keys if null.
        """
        if os.path.isfile('./jamf.pickle') is False:
            self.save_keys()
        else:
            pickle_in = open("jamf.pickle", "rb")
            keys = pickle.load(pickle_in)
            self.casper_system_url = keys["Casper URL"]
            self.casper_username = keys["Casper User"]
            self.casper_password = keys["Casper Pass"]

    def save_keys(self):
        """
        If the pickle doesn't exist on first run, generate it.
        """
        print("Please provide your JAMF JSS API Information...\n")
        print("Public Test API: 'https://tryitout.jamfcloud.com'")
        print("If using the test API, supply '' for username and password.\n")
        casper_url  = input("Please provide your Casper URL (use quotes): ")
        casper_user = input("Please provide your Casper Username (use quotes): ")
        casper_pass = input("Please provide your Casper Password (use quotes): ")

        dicts = {"Casper URL": casper_url, "Casper User": casper_user, "Casper Pass": casper_pass}

        pickle_out = open("jamf.pickle", "wb")
        pickle.dump(dicts, pickle_out)
        pickle_out.close()

        print("Now re-run the script.")
        sys.exit(2)

    def http_get(self, _type):
        """
        Performs HTTP GET and returns JSON response body
        """
        url = '%s/JSSResource/%s' % (self.casper_system_url, _type)

        response = requests.get(url,
                                auth=(self.casper_username, self.casper_password),
                                headers={'Accept': 'application/json'})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print "An error occurred during communication with Casper: '%s'" % e.message
            sys.exit(2)
        return response.json()

    def get_network_list(self):
        """
        Grab the list of managed networks from Casper
        """
        network_data = []
        for x in self.http_get('networksegments')['network_segments']:
            network_data.append(network_obj(
                x['id'],
                x['name'],
                x['starting_address'],
                x['ending_address']
                ))

        return network_data

    def get_device_count(self, _type):
        return len(self.get_the_list_of_devices(_type))

    def get_device_info(self, _type, _id):
        """
        This method is used to retrieve the data about {_type} device {_id} from Casper
        """
        return self.http_get('%s/id/%s' % (_type, _id))

    def get_the_list_of_devices(self, _type):
        """
        This method is used to retrieve the list of {_type} devices from Casper
        """
        if _type is 'mobiledevices':
            json_tag = 'mobile_devices'
        else:
            json_tag = _type

        return [_['id'] for _ in self.http_get(_type)[json_tag]]

    def get_mdm_data(self, _type):
        from time import sleep
        mdm_data = []
        mdm_hosts = self.get_the_list_of_devices(_type)
        
        for x in mdm_hosts[:5]: # Only pulling in the first 15 devices
        # for x in mdm_hosts:
            data = self.get_device_info(_type, x)

            if _type is 'computers':
                mdm_data.append(mdm_host(
                    data['computer']['general']['name'],
                    data['computer']['general']['serial_number'],
                    data['computer']['general']['last_reported_ip'],
                    data['computer']['general']['mac_address'],
                    data['computer']['hardware']['model'],
                    data['computer']['hardware']['model_identifier'],
                    data['computer']['hardware']['os_name'],
                    data['computer']['hardware']['os_version'],
                    data['computer']['hardware']['os_build']))
            
            if _type is 'mobiledevices':
                mdm_data.append(mdm_host(
                    data['mobile_device']['general']['name'],
                    data['mobile_device']['general']['serial_number'],
                    data['mobile_device']['general']['ip_address'],
                    data['mobile_device']['general']['wifi_mac_address'],
                    data['mobile_device']['general']['model'],
                    data['mobile_device']['general']['model_identifier'],
                    data['mobile_device']['general']['os_type'],
                    data['mobile_device']['general']['os_version'],
                    data['mobile_device']['general']['os_build']))                

            sleep(.25) # Put this in for the public JAMF test API. Rate limiting may not occur on local installs.

        return mdm_data