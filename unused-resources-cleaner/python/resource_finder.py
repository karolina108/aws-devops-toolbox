import boto3
import sys
from datetime import datetime, timezone
from utils import get_region_names, write_to_csv
from ec2_resources import get_instances, find_stopped_instances
from resource_reports import create_instances_report

def main():
    session = boto3.Session()
    region_names = get_region_names(session)

    instances = get_instances(session, region_names)

    stopped_instances = find_stopped_instances(instances)
    stopped_instances_report = create_instances_report(stopped_instances)

    now = datetime.now(timezone.utc)

    filename = 'report-{}'.format(now.strftime("%Y%m%d-%H%M%S"))
    if len(sys.argv) == 1:
        file_path = 'output/{}'.format(filename)
    else:
        file_path = '{}/{}'.format(sys.argv[1], filename)

    write_to_csv(stopped_instances_report, file_path)

if __name__ == '__main__':
    main()
