import boto3

def get_region_names(session):
    ec2 = session.client('ec2', region_name='us-east-1')
    regions = ec2.describe_regions()['Regions']
    region_names = [region['RegionName'] for region in regions]
    return region_names

def enrich_with_region(resource, region):
    if 'Region' not in resource.keys():
        resource['Region'] = region
