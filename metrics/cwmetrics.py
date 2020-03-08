import boto3
import random
import string
from datetime import datetime
from common.utils import enrich_with_region

def get_all_metrics_list(session, regions):
    metrics = []

    for region in regions:
        cw = session.client('cloudwatch', region_name=region)
        result = cw.list_metrics()

        for metric in result['Metrics']:
            metric = enrich_with_region(metric, region)
            metrics.append(metric)

        while 'NextPageToken' in result.keys():
            token = result['NextPageToken']
            result = cw.list_metrics(NextPageToken=token)

            for metric in result['Metrics']:
                metric = enrich_with_region(metric, region)
                metrics.append(metric)
    return metrics

def find_metrics_by_dimension_value(metrics, dimension_value):
    return list(filter(
        lambda metric: len(list(filter(lambda dimension: dimension['Value'] == dimension_value,
            metric['Dimensions']))) > 0, metrics))

def find_metrics_by_name(metrics, namespace, metric_name):
    return list(filter(
        lambda metric: metric['Namespace'] == namespace and metric['MetricName'] == metric_name,
            metrics))

def find_metrics_by_namespace(metrics, namespace):
    return list(filter(
        lambda metric: metric['Namespace'] == namespace,
            metrics))

def find_max_dimensions_number(metrics):
    lengths = sorted(metrics, key=lambda metric: len(metric['Dimensions']), reverse=True)
    if len(lengths) > 0:
        return len(lengths[0]['Dimensions'])
    return 0

def filter_no_datapoints(statistics):
    return list(filter(
        lambda statistic: len(statistic['Datapoints']) > 0, statistics
    ))

def filter_metrics_for_region(metrics, region):
    return list(filter(
        lambda metric: metric['Region'] == region, metrics
    ))

def get_metric_statistics(session, region, metrics, period, start_time, end_time):
    stats = []

    cw = session.client('cloudwatch', region_name=region)
    statistics = ['SampleCount', 'Average', 'Sum', 'Minimum', 'Maximum']

    regional_metrics = filter_metrics_for_region(metrics, region)

    for metric in regional_metrics:
        dimensions_label = '.'.join('{}.{}'.format(dimension['Name'], dimension['Value']) for dimension in metric['Dimensions'])

        label = '{}.{}.{}'.format(
                    metric['Namespace'],
                    metric['MetricName'],
                    dimensions_label)

        datapoints = []

        result = cw.get_metric_statistics(
            Namespace=metric['Namespace'],
            MetricName=metric['MetricName'],
            Dimensions=metric['Dimensions'],
            Statistics=statistics,
            StartTime=start_time,
            EndTime=end_time,
            Period=period
        )

        datapoints += result['Datapoints']

        while 'NextPageToken' in result.keys():
            token = result['NextPageToken']

            result = cw.get_metric_statistics(
                Namespace=metric['Namespace'],
                MetricName=metric['MetricName'],
                Dimensions=metric['Dimensions'],
                Statistics=statistics,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                NextPageToken=token
            )
            datapoints += result['Datapoints']

        metric_stats = {
            'Label': label,
            'Region': region,
            'CWLabel': result['Label'],
            'Datapoints': datapoints
        }

        stats.append(metric_stats)

    return filter_no_datapoints(stats)

def prepare_metrics_stats_report(metrics_stats, dimensions_number):

    header = [
        'Namespace',
        'MetricName',
        'Dimensions',
        'Timestamp',
        'FormattedTimestamp'
        'SampleCount',
        'Average',
        'Sum',
        'Minimum',
        'Maximum',
        'Unit',
        'Region'
    ]

    rows = []

    for metric_stat in metrics_stats:
        label = metric_stat['Label'].split('.', 2)

        datapoints = sorted(metric_stat['Datapoints'],
            key=lambda datapoint: datapoint['Timestamp'])

        for datapoint in datapoints:
            row = []
            row += label

            timestamp = datetime.timestamp(datapoint['Timestamp'])
            row.append(timestamp)

            formatted_timestamp = datapoint['Timestamp'].isoformat(' ', 'seconds')
            row.append(formatted_timestamp)

            row.append(datapoint['SampleCount'])
            row.append(datapoint['Average'])
            row.append(datapoint['Sum'])
            row.append(datapoint['Minimum'])
            row.append(datapoint['Maximum'])
            row.append(datapoint['Unit'])
            row.append(metric_stat['Region'])

            rows.append(row)

    name = 'metrics-report'
    report = {'name': name, 'header': header, 'rows': rows}

    return report
