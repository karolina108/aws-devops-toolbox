import boto3
import json
import csv

def get_aws_cost_and_usage(session, start_date, end_date, granularity,
    filter, metrics, group_by):

    ce = session.client('ce')

    items = []

    costs_and_usage = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity=granularity,
        Filter=filter,
        Metrics=metrics,
        GroupBy=group_by
    )

    items += costs_and_usage['ResultsByTime']

    while 'NextPageToken' in costs_and_usage.keys():

        token = costs_and_usage['NextPageToken'];

        costs_and_usage = ce.get_cost_and_usage(
            NextPageToken=token,
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Filter=filter,
            Metrics=metrics,
            GroupBy=group_by)

        items += costs_and_usage['ResultsByTime']

    return {'items' : items, 'definitions': costs_and_usage['GroupDefinitions']}

def create_filter(filter_type, filter_key, values):
    return {
        filter_type : {
            'Key': filter_key,
            'Values': values
        }
    }

def create_group_by(type, key):
    return {
        'Type': type,
        'Key': key
    }

def combine_group_by(group_by):
    if len(group_by) > 2:
        raise Exception('Max value of group by dimensions or tags is 2')
    return group_by

def combine_filters(filters):
    return {
        'And': [filters]
    }

def prepare_cost_metrics_report(items, group_by, metrics, report_name):
    rows = []

    header = [
            'StartDate',
            'EndDate'
        ]

    for group in group_by:
        lower_cased = list(map(lambda word: word.lower(), group['Key'].split('_')))
        upper_cased = list(map(lambda word: ''.join([word[0].upper(), word[1:]]), lower_cased))
        joined = ''.join(upper_cased)
        header.append(joined)

    for metric in metrics:
        header.append(metric)
        header.append(''.join((metric, 'Unit')))

    header.append('IsEstimated')

    for item in items:
        records = item['Groups']
        for record in records:
            row = [
                item['TimePeriod']['Start'],
                item['TimePeriod']['End'],
            ]

            for key in record['Keys']:
                row.append(key)

            for metric in metrics:
                row.append(float(record['Metrics'][metric]['Amount']))
                row.append(record['Metrics'][metric]['Unit'])

            row.append(item['Estimated'])

            rows.append(row)

    report = {'name': report_name, 'header': header, 'rows': rows}

    return report
