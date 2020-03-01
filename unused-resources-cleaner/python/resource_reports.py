import csv

def create_instances_report(instances):
    header = [
        'Instance ID',
        'Instance Type',
        'Instance status',
        'Public IP'
    ]

    rows = []

    for instance in instances:

        row = [
                instance['InstanceId'],
                instance['InstanceType'],
                instance['State']['Name'],
                instance['PublicIpAddress'] if 'PublicIpAddress' in instance.keys() else '-'
            ]
        rows.append(row)
    report = {'header': header, 'rows': rows}
    return report
