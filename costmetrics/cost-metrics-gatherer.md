# Cost metrics gatherer

Cost metrics gatherer gathers gathers cost and usage data.

By default it produces 3 cost and usage reports:

1. Monthly costs for an account
2. Monthly costs of services
3. Monthly costs and usage, grouped by service and usage type

All three reports are exported to csv files.

Then the import the data to a spreadsheet and make pivot tables or use [PivotTable](https://pivottable.js.org/examples/)

## Usage

`awsume` a role that allows access to cost explorer.

`pipenv install`

then:

`pipenv shell`

`python costmetrics.py ${start_date} ${end_date}`

for monthly and daily granularity the start_date and end_date format should be `yyyy-MM-dd`