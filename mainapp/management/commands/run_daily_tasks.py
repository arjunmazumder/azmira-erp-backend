from django.core.management.base import BaseCommand
from mainapp.tasks import auto_mark_absent, generate_monthly_summary
from django.utils import timezone

class Command(BaseCommand):
    help = 'Daily attendance tasks manually run'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        # auto absent/present
        result = auto_mark_absent()
        self.stdout.write(f'auto_mark_absent: {result}')

        # মাসের ১ তারিখ হলে summary generate
        if today.day == 1:
            result = generate_monthly_summary()
            self.stdout.write(f'generate_monthly_summary: {result}')