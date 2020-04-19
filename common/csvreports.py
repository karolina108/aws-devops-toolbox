import csv
from datetime import datetime, timezone

def create_file_path(report_name, output_folder):
    now = datetime.now(timezone.utc)

    filename = '{}-{}.csv'.format(report_name, now.strftime("%Y%m%d-%H%M%S"))
    file_path = '{}/{}'.format(output_folder, filename)

    return file_path

def write_to_csv(report, output_folder):

    filename = '{}'.format(report.get('name', 'report'))

    file_path = create_file_path(filename, output_folder)

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(report['header'])
        writer.writerows(report['rows'])