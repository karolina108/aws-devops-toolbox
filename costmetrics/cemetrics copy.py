import boto3
import json
import csv

session = boto3.Session()
ce = session.client('ce')

start_date = '2019-02-01'
end_date = '2020-01-15'
granularity = 'MONTHLY'

RECORD_TYPE_FILTER = {'Dimensions': {'Key': 'RECORD_TYPE', 'Values': ['Usage']}}
SERVICE_FILTER={
    'And': [
        {
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': []
            }
        },
        {
            'Dimensions': {
                'Key': 'RECORD_TYPE',
                'Values': []
            }
        },
        {
            'Dimensions': {
                'Key': 'LINKED_ACCOUNT',
                'Values': []
            }
        }
    ]
}
COST_METRICS = ['BlendedCost', 'UnblendedCost']
COST_AND_USAGE_METRICS = ['BlendedCost', 'UnblendedCost', 'UsageQuantity']
SERVICE_DIMENSION = {'Type': 'DIMENSION', 'Key': 'SERVICE'}
USAGE_TYPE_DIMENSION = {'Type': 'DIMENSION','Key': 'USAGE_TYPE'}
RECORD_TYPE_DIMENSION = {'Type': 'DIMENSION','Key': 'RECORD_TYPE'}
LINKED_ACCOUNT_DIMENSION = {'Type': 'DIMENSION','Key': 'LINKED_ACCOUNT'}
CFN_TAG_DIMENSION = {'Type': 'TAG','Key': 'aws:cloudformation:stack-id'}

def get_aws_cost_and_usage(ce_client, start_date, end_date, granularity,
    filter, metrics, dimensions):

    items = []

    costs_and_usage = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity=granularity,
        Filter=filter,
        Metrics=metrics,
        GroupBy=dimensions
    )

    items += costs_and_usage['ResultsByTime']

    while 'NextPageToken' in costs_and_usage.keys():

        token = costs_and_usage['NextPageToken'];

        costs_and_usage = ce_client.get_cost_and_usage(
            NextPageToken=token,
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Filter=filter,
            Metrics=metrics,
            GroupBy=dimensions)

        items += costs_and_usage['ResultsByTime']
    return {'items' : items, 'definitions': costs_and_usage['GroupDefinitions']}

def get_aws_cost_and_usage_unfiltered(ce_client, start_date, end_date, granularity,
    metrics, dimensions):

    items = []

    costs_and_usage = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity=granularity,
        Metrics=metrics,
        GroupBy=dimensions
    )

    items += costs_and_usage['ResultsByTime']

    while 'NextPageToken' in costs_and_usage.keys():

        token = costs_and_usage['NextPageToken'];

        costs_and_usage = ce_client.get_cost_and_usage(
            NextPageToken=token,
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Metrics=metrics,
            GroupBy=dimensions)

        items += costs_and_usage['ResultsByTime']
    return {'items' : items, 'definitions': costs_and_usage['GroupDefinitions']}

def get_costs_by_tag(ce_client, start_date, end_date, granularity, tag):

    tag_dimension = {'Type': 'TAG','Key': tag}

    result = get_aws_cost_and_usage(
        ce_client=ce,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=RECORD_TYPE_FILTER,
        metrics=COST_METRICS,
        dimensions=[tag_dimension])

    rows = []
    header = [
            'start_date',
            'end_date',
            'tag_key',
            'tag_value',
            'blended_cost_amount',
            'blended_cost_unit',
            'unblended_cost_amount',
            'unblended_cost_unit',
            'estimated'
        ]

    items = result['items']
    definitions = result['definitions']

    for item in items:
        records = item['Groups']
        for record in records:
            row = [
                item['TimePeriod']['Start'],
                item['TimePeriod']['End'],
                definitions[0]['Key'],
                record['Keys'][0],
                float(record['Metrics']['BlendedCost']['Amount']),
                record['Metrics']['BlendedCost']['Unit'],
                float(record['Metrics']['UnblendedCost']['Amount']),
                record['Metrics']['UnblendedCost']['Unit'],
                item['Estimated']
            ]
            rows.append(row)

    return {'header': header, 'items': rows}

def get_cost_and_usage_by_service(ce_client, start_date, end_date, granularity):

    result = get_aws_cost_and_usage(
        ce_client=ce,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=RECORD_TYPE_FILTER,
        metrics=COST_METRICS,
        dimensions=[SERVICE_DIMENSION])

    rows = []
    header = [
            'start_date',
            'end_date',
            'first_dimension_name',
            'first_dimension',
            'blended_cost_amount',
            'blended_cost_unit',
            'unblended_cost_amount',
            'unblended_cost_unit',
            'estimated'
        ]

    items = result['items']
    definitions = result['definitions']

    for item in items:
        records = item['Groups']
        for record in records:
            row = [
                item['TimePeriod']['Start'],
                item['TimePeriod']['End'],
                definitions[0]['Key'],
                record['Keys'][0],
                float(record['Metrics']['BlendedCost']['Amount']),
                record['Metrics']['BlendedCost']['Unit'],
                float(record['Metrics']['UnblendedCost']['Amount']),
                record['Metrics']['UnblendedCost']['Unit'],
                item['Estimated']
            ]
            rows.append(row)

    return {'header': header, 'items': rows}

def get_cost_and_usage_for_service(ce_client, start_date, end_date, granularity, service):

    service_filter={
        'And': [
            {
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': [
                        service
                    ]
                }
            },
            {
                'Dimensions': {
                    'Key': 'RECORD_TYPE',
                    'Values': ['Usage']
                }
            }
        ]
    }

    result = get_aws_cost_and_usage(
        ce_client=ce,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=service_filter,
        metrics=COST_AND_USAGE_METRICS,
        dimensions=[SERVICE_DIMENSION, USAGE_TYPE_DIMENSION])

    rows = []
    header = [
            'start_date',
            'end_date',
            'first_dimension_name',
            'first_dimension',
            'second_dimension_name',
            'second_dimension',
            'blended_cost_amount',
            'blended_cost_unit',
            'unblended_cost_amount',
            'unblended_cost_unit',
            'usage_amount',
            'usage_amount_unit',
            'estimated'
        ]

    items = result['items']
    definitions = result['definitions']

    for item in items:
        records = item['Groups']
        for record in records:
            row = [
                item['TimePeriod']['Start'],
                item['TimePeriod']['End'],
                definitions[0]['Key'],
                record['Keys'][0],
                definitions[1]['Key'],
                record['Keys'][1],
                float(record['Metrics']['BlendedCost']['Amount']),
                record['Metrics']['BlendedCost']['Unit'],
                float(record['Metrics']['UnblendedCost']['Amount']),
                record['Metrics']['UnblendedCost']['Unit'],
                float(record['Metrics']['UsageQuantity']['Amount']),
                record['Metrics']['UsageQuantity']['Unit'],
                item['Estimated']
            ]
            rows.append(row)

    return {'header': header, 'items': rows}

def get_cost_and_usage_by_service_and_usage_type(ce_client, start_date, end_date, granularity):
    result = get_aws_cost_and_usage(
        ce_client=ce,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        filter=RECORD_TYPE_FILTER,
        metrics=COST_AND_USAGE_METRICS,
        dimensions=[SERVICE_DIMENSION, USAGE_TYPE_DIMENSION])

    rows = []
    header = [
            'start_date',
            'end_date',
            'first_dimension_name',
            'first_dimension',
            'second_dimension_name',
            'second_dimension',
            'blended_cost_amount',
            'blended_cost_unit',
            'unblended_cost_amount',
            'unblended_cost_unit',
            'usage_amount',
            'usage_amount_unit',
            'estimated'
        ]

    items = result['items']
    definitions = result['definitions']

    for item in items:
        records = item['Groups']
        for record in records:
            row = [
                item['TimePeriod']['Start'],
                item['TimePeriod']['End'],
                definitions[0]['Key'],
                record['Keys'][0],
                definitions[1]['Key'],
                record['Keys'][1],
                float(record['Metrics']['BlendedCost']['Amount']),
                record['Metrics']['BlendedCost']['Unit'],
                float(record['Metrics']['UnblendedCost']['Amount']),
                record['Metrics']['UnblendedCost']['Unit'],
                float(record['Metrics']['UsageQuantity']['Amount']),
                record['Metrics']['UsageQuantity']['Unit'],
                item['Estimated']
            ]
            rows.append(row)

    return {'header': header, 'items': rows}

def get_costs_by_record_type(ce_client, start_date, end_date, granularity):
    result = get_aws_cost_and_usage_unfiltered(
        ce_client=ce,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        metrics=COST_METRICS,
        dimensions=[RECORD_TYPE_DIMENSION])

    rows = []
    header = [
            'start_date',
            'end_date',
            'first_dimension_name',
            'first_dimension',
            'blended_cost_amount',
            'blended_cost_unit',
            'unblended_cost_amount',
            'unblended_cost_unit',
            'estimated'
        ]

    items = result['items']
    definitions = result['definitions']

    for item in items:
        records = item['Groups']
        for record in records:
            row = [
                item['TimePeriod']['Start'],
                item['TimePeriod']['End'],
                definitions[0]['Key'],
                record['Keys'][0],
                float(record['Metrics']['BlendedCost']['Amount']),
                record['Metrics']['BlendedCost']['Unit'],
                float(record['Metrics']['UnblendedCost']['Amount']),
                record['Metrics']['UnblendedCost']['Unit'],
                item['Estimated']
            ]
            rows.append(row)

    return {'header': header, 'items': rows}

costs_and_usage = get_cost_and_usage_by_service_and_usage_type(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity
)

with open('../output/py-costs-by-service-and-usage-type.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_cost_and_usage_by_service(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity
)

with open('../output/py-costs-by-service.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_costs_by_record_type(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity
)

with open('../output/py-costs-by-record-type.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_costs_by_tag(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity,
    tag='expiration-date'
)

with open('../output/py-costs-by-tag-expiration-date.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_cost_and_usage_for_service(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity,
    service='AmazonCloudWatch'
)

with open('../output/py-costs-for-service.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])


# DAILY
granularity = 'DAILY'

costs_and_usage = get_cost_and_usage_by_service_and_usage_type(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity
)

with open('../output/py-costs-by-service-and-usage-type-daily.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_cost_and_usage_by_service(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity
)

with open('../output/py-costs-by-service-daily.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_costs_by_record_type(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity
)

with open('../output/py-costs-by-record-type-daily.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_costs_by_tag(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity,
    tag='expiration-date'
)

with open('../output/py-costs-by-tag-expiration-date-daily.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])

costs_and_usage = get_costs_by_tag(
    ce_client=ce,
    start_date=start_date,
    end_date=end_date,
    granularity=granularity,
    tag='aws:cloudformation:stack-id'
)

with open('../output/py-costs-by-tag-stack-id-daily.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(costs_and_usage['header'])
    writer.writerows(costs_and_usage['items'])
