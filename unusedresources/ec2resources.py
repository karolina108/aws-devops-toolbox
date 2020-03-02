import boto3

def get_instances(session, regions):
    instances = []

    for region in regions:
        ec2 = session.client('ec2', region_name=region)
        reservations = ec2.describe_instances()['Reservations']

        if len(reservations) != 0:
            instance_list = reservations[0]['Instances']
            for instance in instance_list:
                instance['Region'] = region
                instances.append(instance)

    return instances

def get_public_ip_addresses(session, regions):
    ip_addresses = []

    for region in regions:
        ec2 = session.client('ec2', region_name=region)
        addresses = ec2.describe_addresses()['Addresses']

        for address in addresses:
            if 'PublicIp' in address.keys():
                address['Region'] = region
                ip_addresses.append(address)

    return ip_addresses

def get_network_interfaces(session, regions):
    network_interfaces = []

    for region in regions:
        ec2 = session.client('ec2', region_name=region)
        interfaces = ec2.describe_network_interfaces()['NetworkInterfaces']

        for interface in interfaces:
            interface['Region'] = region
            network_interfaces.append(interface)

    return network_interfaces

def find_stopped_instances(instances):
    stopped_instances = list(filter(
        lambda instance: instance['State']['Name'] == 'stopped', instances))
    return stopped_instances

def find_unused_public_ip_addresses(addresses, instances, interfaces):
    unused_addresses = []

    unused_interfaces_with_public_ip = list(filter(
        lambda interface: 'Association' in interface.keys() and
        'PublicIp' in interface['Association'].keys() and
        interface['Status'] != 'in-use', interfaces))

    used_interfaces_with_public_ip = list(filter(
        lambda interface: 'Association' in interface.keys() and
        'PublicIp' in interface['Association'].keys() and
        interface['Status'] == 'in-use', interfaces))

    unused_instances = list(filter(
        lambda instance: instance['State']['Name'] != 'running', instances))

    for address in addresses:
        if 'AssociationId' not in address.keys():
            address['Comment'] = 'Not associated'.format(address['PublicIp'])
            unused_addresses.append(address)
        else:
            for interface in unused_interfaces_with_public_ip:
                if interface['Association']['PublicIp'] == address['PublicIp']:
                    address['Comment'] = 'Associated with available ENI: {}'.format(interface['NetworkInterfaceId'])
                    unused_addresses.append(address)

            for interface in used_interfaces_with_public_ip:
                if interface['Association']['PublicIp'] == address['PublicIp']:
                    for instance in unused_instances:
                        if 'InstanceId' in interface['Attachment'].keys() and interface['Attachment']['InstanceId'] == instance['InstanceId']:
                            address['Comment'] = 'Associated with not running instance {}'.format(instance['InstanceId'])
                            unused_addresses.append(address)

    return unused_addresses

def prepare_stopped_instances_data(session, regions):
    instances = get_instances(session, regions)
    stopped_instances = find_stopped_instances(instances)
    return stopped_instances

def prepare_unused_eips_data(session, regions):
    instances = get_instances(session, regions)
    addresses = get_public_ip_addresses(session, regions)
    interfaces = get_network_interfaces(session, regions)
    unused_addresses = find_unused_public_ip_addresses(addresses, instances, interfaces)
    return unused_addresses

def prepare_instances_report(instances):
    header = [
        'Instance ID',
        'Instance Type',
        'Instance status',
        'Public IP',
        'Region'
    ]

    rows = []

    for instance in instances:
        row = [
                instance['InstanceId'],
                instance['InstanceType'],
                instance['State']['Name'],
                instance['PublicIpAddress'] if 'PublicIpAddress' in instance.keys() else '-',
                instance['Region']
            ]
        rows.append(row)
    name = 'stopped-instances-report'
    report = {'name': name, 'header': header, 'rows': rows}
    return report

def prepare_unused_eip_report(addresses):
    header = [
        'IP Address',
        'Network Interface ID',
        'Instance ID',
        'Region',
        'Comment'
    ]

    rows = []

    for address in addresses:
        row = [
            address['PublicIp'],
            address['NetworkInterfaceId'] if 'NetworkInterfaceId' in address.keys() else '-',
            address['InstanceId'] if 'InstanceId' in address.keys() else '-',
            address['Region'] if 'Region' in address.keys() else '-',
            address['Comment'] if 'Comment' in address.keys() else '-'
        ]
        rows.append(row)
    name = 'unused-eips-report'
    report = {'name': name, 'header': header, 'rows': rows}
    return report