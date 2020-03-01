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

def find_stopped_instances(instances):
    stopped_instances = list(filter(
        lambda instance: instance['State']['Name'] == 'stopped', instances))
    return stopped_instances



