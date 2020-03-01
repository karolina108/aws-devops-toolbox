import csv
from datetime import datetime, timezone

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

def create_file_path(report_name, output_folder):
    now = datetime.now(timezone.utc)

    filename = '{}-{}'.format(report_name, now.strftime("%Y%m%d-%H%M%S"))
    file_path = '{}/{}'.format(output_folder, filename)

    return file_path

def write_to_csv(report, output_folder):

    file_path = create_file_path(report['name'], output_folder)

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(report['header'])
        writer.writerows(report['rows'])