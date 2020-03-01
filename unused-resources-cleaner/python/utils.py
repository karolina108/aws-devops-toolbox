import boto3
import csv

def get_region_names(session):
    ec2 = session.client('ec2', region_name='us-east-1')
    regions = ec2.describe_regions()['Regions']
    region_names = [region['RegionName'] for region in regions]
    return region_names

def write_to_csv(report, file_path):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(report['header'])
        writer.writerows(report['rows'])


