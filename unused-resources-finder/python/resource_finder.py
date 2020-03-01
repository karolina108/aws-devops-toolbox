import boto3
import sys

from utils import get_region_names
from ec2_resources import *
from csv_reports import *

def main():
    session = boto3.Session()
    regions = get_region_names(session)

    if len(sys.argv) == 1:
        output_folder = 'output'
    else:
        output_folder = '{}'.format(sys.argv[1], filename)

    stopped_instances = prepare_stopped_instances_data(session, regions)
    stopped_instances_report = prepare_instances_report(stopped_instances)
    write_to_csv(stopped_instances_report, output_folder)

    unused_eips = prepare_unused_eips_data(session, regions)
    unused_eip_report = prepare_unused_eip_report(unused_eips)
    write_to_csv(unused_eip_report, output_folder)

if __name__ == '__main__':
    main()
