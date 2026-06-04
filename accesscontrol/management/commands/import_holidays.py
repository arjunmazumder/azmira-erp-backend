# management/commands/import_holidays.py
from django.core.management.base import BaseCommand
from mainapp.models import ERPHoliday
import csv

class Command(BaseCommand):
    help = 'CSV থেকে holidays import করো'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs['csv_file']) as f:
            reader = csv.DictReader(f)
            count  = 0
            for row in reader:
                ERPHoliday.objects.get_or_create(
                    date         = row['date'],       # format: 2025-03-26
                    defaults={
                        'name'        : row['name'],
                        'holiday_type': row.get('type', 'govt'),
                    }
                )
                count += 1
        self.stdout.write(f'{count} holidays imported.')