from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta, time
from calendar import monthrange
from django.db import models as django_models

OFFICE_START_TIME = time(9, 0, 0)


def is_holiday(check_date: date) -> bool:
    from mainapp.models import ERPHoliday
    # শুক্রবার চেক
    if check_date.weekday() == 4:
        return True
    # Govt holiday চেক
    return ERPHoliday.objects.filter(date=check_date).exists()


@shared_task
def auto_mark_absent():
    from mainapp.models import ERPAttendance, ERPEmployee

    today     = timezone.localdate()
    employees = ERPEmployee.objects.select_related('user').filter(user__is_active=True)
    result    = {'holiday': [], 'absent': []}

    for employee in employees:
        existing = ERPAttendance.objects.filter(
            employee        = employee,
            attendance_date = today,
        ).first()

        # check-in দিয়েছে → skip
        if existing and existing.check_in:
            continue

        if is_holiday(today):
            ERPAttendance.objects.update_or_create(
                employee        = employee,
                attendance_date = today,
                defaults={
                    'status'    : 'holiday',
                    'marked_by' : 'System (Auto-Holiday)',
                }
            )
            result['holiday'].append(employee.employee_code)
        else:
            ERPAttendance.objects.update_or_create(
                employee        = employee,
                attendance_date = today,
                defaults={
                    'status'    : 'absent',
                    'marked_by' : 'System (Auto-Absent)',
                }
            )
            result['absent'].append(employee.employee_code)

    return (
        f"Holiday: {len(result['holiday'])} → {result['holiday']} | "
        f"Absent: {len(result['absent'])} → {result['absent']}"
    )


@shared_task
def generate_monthly_summary(year: int = None, month: int = None):
    from mainapp.models import ERPAttendance, ERPAttendanceSummary, ERPEmployee

    today = timezone.localdate()
    if not year or not month:
        first_of_this_month = today.replace(day=1)
        last_month          = first_of_this_month - timedelta(days=1)
        year, month         = last_month.year, last_month.month

    month_start   = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    employees     = ERPEmployee.objects.select_related('user').filter(user__is_active=True)

    for employee in employees:
        attendances = ERPAttendance.objects.filter(
            employee               = employee,
            attendance_date__year  = year,
            attendance_date__month = month,
        )
        ERPAttendanceSummary.objects.update_or_create(
            employee = employee,
            month    = month_start,
            defaults = {
                'total_days'   : days_in_month,
                'present_days' : attendances.filter(status='present').count(),
                'absent_days'  : attendances.filter(status='absent').count(),
                'late_days'    : attendances.filter(status='late').count(),
                'half_days'    : attendances.filter(status='half_day').count(),
                'leave_days'   : attendances.filter(status='leave').count(),
                'holiday_days' : attendances.filter(status='holiday').count(),
                'total_hours'  : attendances.aggregate(
                                     total=django_models.Sum('total_hours')
                                 )['total'] or 0,
            }
        )

    return f'Summary done: {month_start.strftime("%B %Y")}'
    """
    প্রতি মাসের ১ তারিখে আগের মাসের summary তৈরি।
    """
    from mainapp.models import ERPAttendance, ERPAttendanceSummary, ERPEmployee

    today = timezone.localdate()

    if not year or not month:
        first_of_this_month = today.replace(day=1)
        last_month          = first_of_this_month - timedelta(days=1)
        year, month         = last_month.year, last_month.month

    month_start   = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    employees     = ERPEmployee.objects.select_related('user').filter(user__is_active=True)

    for employee in employees:
        attendances = ERPAttendance.objects.filter(
            employee               = employee,
            attendance_date__year  = year,
            attendance_date__month = month,
        )

        ERPAttendanceSummary.objects.update_or_create(
            employee = employee,
            month    = month_start,
            defaults = {
                'total_days'   : days_in_month,
                'present_days' : attendances.filter(status='present').count(),
                'absent_days'  : attendances.filter(status='absent').count(),
                'late_days'    : attendances.filter(status='late').count(),
                'half_days'    : attendances.filter(status='half_day').count(),
                'leave_days'   : attendances.filter(status='leave').count(),
                'holiday_days' : attendances.filter(status='holiday').count(),
                'total_hours'  : attendances.aggregate(
                                     total=django_models.Sum('total_hours')
                                 )['total'] or 0,
            }
        )

    return f'Summary done: {month_start.strftime("%B %Y")}'