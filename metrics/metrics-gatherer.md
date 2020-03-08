# Gathering CloudWatch metrics from AWS Account

MetricsGatherer collects metrics statistics from your AWS Account. By default it gathers all available metrics in all regions in 1-hour resolution and writes them to a CSV file.

Statistics:

- SampleCount
- Average
- Sum
- Minimum
- Maximum

## Usage

`pipenv shell`

`python metrics-gatherer.py` - for default resolution

`python metrics-gatherer.py resolution` - for required resolution

Possible values of the `resolution` argument:

- `1_minute`
- `5_minutes`
- `1_hour`
- `3_hours`
- `6_hours`
- `1_day`
- `30_days`

By default the metrics are collected till the current day midnight (0:00:00). The start date depends on the chosen resolution and is the current date midnight minus interval. The interval cannot be higher than metrics retention in CloudWatch. See the table below for details:

| resolution  | period (seconds)   | interval (days)   | retention (days)   |
| :---------- | ----------------: | :---------------: | :----------------: |
| 1 minute    | 60                 | 1                 | 15                 |
| 5 minutes   | 300                | 5                 | 63                 |
| 1 hour      | 3.600              | 60                | 455                |
| 3 hours     | 10.800             | 180               | 455                |
| 6 hours     | 21.600             | 360               | 455                |
| 1 day       | 86.400             | 455               | 455                |
| 30 days     | 2.592.000          | 455               | 455                |

Note: for some environments the generated files may be large. Consider then modifying the `metrics-gatherer.py` to use:

- only selected regions
- shorter time ranges
- metrics limited by namespace, metric name or dimension value

The list of metrics & dimensions for supported AWS Services can be found in documentation:

[AWS Services That Publish CloudWatch Metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html)
