from plugins.casper import CasperConnection

casper = CasperConnection()

def get_all_counts():
    print 'All Managed Devices : \n------'
    print 'Mobile : %s' % casper.get_device_count('mobiledevices')
    print 'Computers : %s' % casper.get_device_count('computers')
    print 'Peripheral Devices : %s' % casper.get_device_count('peripherals')
    #print 'LDAP Servers : %s' % casper.get_device_count('ldapservers')
    print 'Printers : %s' % casper.get_device_count('printers')
    print '\nAdministrative\n------'
    print 'Buildings : %s' % casper.get_device_count('buildings')
    print 'Departments : %s' % casper.get_device_count('departments')
    print '# of Users : %s' % casper.get_device_count('users')
    print '------\n'

def report_managed_devices(_type):
    mdm_data = casper.get_mdm_data(_type)

    if _type is 'mobiledevices':
        print '\nManaged Mobile Devices : {}\n------'.format(casper.get_device_count(_type))
    if _type is 'computers':
        print '\nManaged Desktops/Laptops : {}\n------'.format(casper.get_device_count(_type))

    for x in range(len(mdm_data)):
        print 'Name : {} (S/N : {})'.format(mdm_data[x].name.encode("utf-8"), mdm_data[x].serial_number)
        print 'Last IP : {} (MAC : {})'.format(mdm_data[x].last_reported_ip, mdm_data[x].mac_address)
        print 'Model : {} ({})'.format(mdm_data[x].model, mdm_data[x].model_identifier)
        print 'OS : {} {} ({})'.format(mdm_data[x].os_name, mdm_data[x].os_version, mdm_data[x].os_build)
        print '------'

def report_managed_networks():
    network_data = casper.get_network_list()
    print 'Managed Networks : {}\n------'.format(len(network_data))

    for x in range(len(network_data)):
        print 'Network : {} (ID: {})'.format(network_data[x].name, network_data[x]._id)
        print 'Ranges :  {} - {}'.format(network_data[x].start_ip, network_data[x].end_ip)
        print '------'

def main():
    """
    Main entry point for Casper sync
    """
    print 'Polling Casper/JAMF API for Information...\n'
    print 'Note: Using public JAMF API. Limiting output to first 5 mobile/pc lookups.\n'

    get_all_counts()

    report_managed_networks()

    report_managed_devices('computers')

    report_managed_devices('mobiledevices')

    return True

if __name__ == '__main__':
    main()