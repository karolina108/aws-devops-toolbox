import csv

def create_instances_report(instances):
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
    report = {'header': header, 'rows': rows}
    return report

def create_unused_eip_report(addresses):
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
    report = {'header': header, 'rows': rows}
    return report

