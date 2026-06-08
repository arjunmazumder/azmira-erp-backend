from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.tasks import (
    auto_mark_absent,
    generate_monthly_summary,
    send_installment_reminder_48h,
    send_installment_due_today,
)


class Command(BaseCommand):
    help = 'সব scheduled task একসাথে run করে'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        self.stdout.write(f'Tasks শুরু: {today}')

        try:
            result = auto_mark_absent()
            self.stdout.write(f'Attendance: {result}')
        except Exception as e:
            self.stdout.write(f'Attendance ERROR: {e}')

        if today.day == 1:
            try:
                result = generate_monthly_summary()
                self.stdout.write(f'Summary: {result}')
            except Exception as e:
                self.stdout.write(f'Summary ERROR: {e}')

        try:
            send_installment_reminder_48h()
            self.stdout.write('48h SMS: done')
        except Exception as e:
            self.stdout.write(f'48h SMS ERROR: {e}')

        try:
            send_installment_due_today()
            self.stdout.write('Due SMS: done')
        except Exception as e:
            self.stdout.write(f'Due SMS ERROR: {e}')

        self.stdout.write('সব task শেষ।')