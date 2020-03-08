import boto3
import sys
from datetime import datetime, date, timedelta
import costmetrics.costmetrics as cm
from common.csvreports import write_to_csv

def main():
    session = boto3.Session()

    start_date = ('2019-12-01')
    end_date = ('2020-03-01')

    # General cost report

    cost_metrics = ['BlendedCost', 'UnblendedCost']
    granularity = 'MONTHLY'

    all_record_type_filter = cm.create_filter('Dimensions', 'RECORD_TYPE',
        ['Usage', 'Credit', 'Tax', 'Refund'])

    record_type_dimension = cm.create_group_by('DIMENSION', 'RECORD_TYPE')
    record_type_group_by = [record_type_dimension]

    record_type_costs = cm.get_aws_cost_and_usage(
        session=session,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=all_record_type_filter,
        metrics=cost_metrics,
        group_by=record_type_group_by
    )['items']

    report_name = 'all_costs_report'
    all_costs_report = cm.prepare_cost_metrics_report(record_type_costs,
        record_type_group_by, cost_metrics, report_name)

    write_to_csv(all_costs_report, output_folder='output')

    # Service costs report

    all_metrics = ['BlendedCost', 'UnblendedCost']
    granularity = 'MONTHLY'

    record_type_filter = cm.create_filter('Dimensions', 'RECORD_TYPE', ['Usage'])

    service_dimesion = cm.create_group_by('DIMENSION', 'SERVICE')
    service_group_by = [service_dimesion]

    service_cost_and_usage = cm.get_aws_cost_and_usage(
        session=session,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=record_type_filter,
        metrics=all_metrics,
        group_by=service_group_by
    )['items']

    report_name = 'service_costs_report'
    service_costs_report = cm.prepare_cost_metrics_report(service_cost_and_usage,
        service_group_by, all_metrics, report_name)

    write_to_csv(service_costs_report, output_folder='output')

    # Service costs & usage report

    all_metrics = ['BlendedCost', 'UnblendedCost', 'UsageQuantity']
    granularity = 'MONTHLY'

    record_type_filter = cm.create_filter('Dimensions', 'RECORD_TYPE', ['Usage'])

    service_dimesion = cm.create_group_by('DIMENSION', 'SERVICE')
    usage_dimension = cm.create_group_by('DIMENSION', 'USAGE_TYPE')
    service_group_by = [service_dimesion, usage_dimension]

    service_cost_and_usage = cm.get_aws_cost_and_usage(
        session=session,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=record_type_filter,
        metrics=all_metrics,
        group_by=service_group_by
    )['items']

    report_name = 'service_costs_usage_report'
    service_costs_usage_report = cm.prepare_cost_metrics_report(service_cost_and_usage,
        service_group_by, all_metrics, report_name)

    write_to_csv(service_costs_usage_report, output_folder='output')


if __name__ == '__main__':
    main()
