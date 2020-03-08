import boto3
import sys
from datetime import datetime, date, timedelta
from common.utils import get_region_names
from common.csvreports import write_to_csv
from metrics.cwmetrics import *


def main():
    session = boto3.Session()
    regions = get_region_names(session)

    available_metrics = get_all_metrics_list(session, regions)
    metrics = available_metrics

    # uncomment for further metrics filtering:

    # metrics = find_metrics_by_name(available_metrics, namespace, metric_name)
    # metrics = find_metrics_by_namespace(available_metrics, namespace)
    # metrics = find_metrics_by_dimension_value(available_metrics, dimension_value)

    periods_for_metrics = {
        '1_minute': {'period': 60, 'interval': 1, 'retention': 15},
        '5_minutes': {'period': 300, 'interval': 5, 'retention': 63},
        '1_hour': {'period': 3600, 'interval': 60, 'retention': 455},
        '3_hours': {'period': 10800, 'interval': 180, 'retention': 455},
        '6_hours': {'period': 21600, 'interval': 360, 'retention': 455},
        '1_day': {'period': 86400, 'interval': 455, 'retention': 455},
        '30_days': {'period': 2592000, 'interval': 455, 'retention': 455}
    }

    if sys.argv[1] and sys.argv[1] in periods_for_metrics.keys() :
        resolution = sys.argv[1]
    else:
        print('Using default resolution: 1 hour')
        resolution = '1_hour'

    period = periods_for_metrics[resolution]['period']
    end_time = datetime.combine(date.today(), datetime.min.time())
    start_time = end_time - timedelta(periods_for_metrics[resolution]['interval'])

    metric_stats = []

    for region in regions:
        regional_stats = get_metric_statistics(session, region, metrics,
            period, start_time, end_time)
        metric_stats += regional_stats

    dimensions_number = find_max_dimensions_number(metrics)
    report = prepare_metrics_stats_report(metric_stats, dimensions_number)
    write_to_csv(report, 'output')

if __name__ == '__main__':
    main()
