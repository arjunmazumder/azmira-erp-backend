from django.core.management.base import BaseCommand
from mainapp.tasks import (
    send_installment_reminder_48h,
    send_installment_due_today,
)

class Command(BaseCommand):
    help = 'SMS reminder tasks manually run'

    def handle(self, *args, **kwargs):
        send_installment_reminder_48h()
        self.stdout.write('48h reminder done')

        send_installment_due_today()
        self.stdout.write('Due today reminder done')