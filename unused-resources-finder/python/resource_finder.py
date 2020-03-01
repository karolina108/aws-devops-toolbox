import boto3
import sys
from datetime import datetime, timezone
from utils import get_region_names, write_to_csv
from ec2_resources import *
from resource_reports import *

def main():
    session = boto3.Session()
    region_names = get_region_names(session)
    now = datetime.now(timezone.utc)

    instances = get_instances(session, region_names)
    stopped_instances = find_stopped_instances(instances)
    stopped_instances_report = create_instances_report(stopped_instances)

    filename = 'stopped-instances-report-{}'.format(now.strftime("%Y%m%d-%H%M%S"))
    if len(sys.argv) == 1:
        file_path = 'output/{}'.format(filename)
    else:
        file_path = '{}/{}'.format(sys.argv[1], filename)

    write_to_csv(stopped_instances_report, file_path)

    addresses = get_public_ip_addresses(session, region_names)
    interfaces = get_network_interfaces(session, region_names)
    unused_addresses = find_unused_public_ip_addresses(addresses, instances, interfaces)
    unused_eip_report = create_unused_eip_report(unused_addresses)

    filename = 'unused-eip-report-{}'.format(now.strftime("%Y%m%d-%H%M%S"))
    if len(sys.argv) == 1:
        file_path = 'output/{}'.format(filename)
    else:
        file_path = '{}/{}'.format(sys.argv[1], filename)

    write_to_csv(unused_eip_report, file_path)

if __name__ == '__main__':
    main()
