# from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta, time
from calendar import monthrange
from django.db import models as django_models
from .models import ERPInstallmentPlan, ERPSMSLog
from .utils.sms import send_sms

OFFICE_START_TIME = time(9, 0, 0)


def is_holiday(check_date: date) -> bool:
    from mainapp.models import ERPHoliday
    if check_date.weekday() == 4:  # শুক্রবার
        return True, 'শুক্রবার'
    holiday = ERPHoliday.objects.filter(date=check_date).first()
    if holiday:
        return True, holiday.name
    return False, None


# @shared_task
def auto_mark_absent():
    from mainapp.models import ERPAttendance, ERPEmployee

    today     = timezone.localdate()
    employees = ERPEmployee.objects.select_related('user').filter(user__is_active=True)
    result    = {'present': [], 'absent': []}

    is_today_holiday, holiday_name = is_holiday(today)

    for employee in employees:
        existing = ERPAttendance.objects.filter(
            employee        = employee,
            attendance_date = today,
        ).first()

        # ইতিমধ্যে check-in করেছে → skip
        if existing and existing.check_in:
            continue

        if is_today_holiday:
            # ✅ শুক্রবার বা ERPHoliday → present mark
            ERPAttendance.objects.update_or_create(
                employee        = employee,
                attendance_date = today,
                defaults={
                    'status'    : 'present',
                    'remarks'   : holiday_name,
                    'marked_by' : f'System (Auto-Present: {holiday_name})',
                }
            )
            result['present'].append(employee.employee_code)

        else:
            # সাধারণ দিনে check-in নেই → absent
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
        f"Auto-Present: {len(result['present'])} → {result['present']} | "
        f"Absent: {len(result['absent'])} → {result['absent']}"
    )

# @shared_task
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

        # ✅ present = actual present + late + half_day + auto-present (friday/holiday)
        present_days = attendances.filter(
            status__in=['present', 'late', 'half_day']
        ).count()

        # ✅ holiday = ERPHoliday বা শুক্রবারে auto-present হয়েছে
        # remarks এ holiday নাম থাকে, marked_by তে 'System (Auto-Present' থাকে
        holiday_days = attendances.filter(
            status='present',
            marked_by__startswith='System (Auto-Present',
        ).count()

        # ✅ actual present = present_days থেকে holiday বাদ দিয়ে
        actual_present = present_days - holiday_days

        ERPAttendanceSummary.objects.update_or_create(
            employee = employee,
            month    = month_start,
            defaults = {
                'total_days'   : days_in_month,
                'present_days' : actual_present,
                'absent_days'  : attendances.filter(status='absent').count(),
                'late_days'    : attendances.filter(status='late').count(),
                'half_days'    : attendances.filter(status='half_day').count(),
                'leave_days'   : attendances.filter(status='leave').count(),
                'holiday_days' : holiday_days,
                'total_hours'  : attendances.aggregate(
                                     total=django_models.Sum('total_hours')
                                 )['total'] or 0,
            }
        )

    return f'Summary done: {month_start.strftime("%B %Y")}'




# @shared_task
def send_installment_reminder_48h():
    target_date = date.today() + timedelta(days=2)

    installments = ERPInstallmentPlan.objects.filter(
        due_date=target_date,
        is_paid=False,
        sms_sent_48h_flag=False
    ).select_related('booking__customer__user')  # ✅ user পর্যন্ত select_related

    for installment in installments:
        customer = installment.booking.customer
        phone    = customer.user.phone        # ✅ customer.phone → customer.user.phone
        name     = customer.user.full_name    # ✅ এটাও user থেকে নিতে হবে
        message  = (
            f"প্রিয় {name}, "
            f"আপনার {installment.amount} টাকার কিস্তি "
            f"{installment.due_date} তারিখে পরিশোধযোগ্য। "
            f"সময়মতো পরিশোধ করুন। - Azmira"
        )

        success, error = send_sms(phone, message)

        ERPSMSLog.objects.create(
            recipient_phone = phone,
            recipient_name  = name,           # ✅
            sms_type        = 'installment_reminder',
            message         = message,
            status          = 'sent' if success else 'failed',
            customer        = customer,
            booking         = installment.booking,
            sent_at         = timezone.now() if success else None,
            error_message   = error or ''
        )

        if success:
            installment.sms_sent_48h_flag = True
            installment.save(update_fields=['sms_sent_48h_flag'])


# @shared_task
def send_installment_due_today():
    today = date.today()

    installments = ERPInstallmentPlan.objects.filter(
        due_date=today,
        is_paid=False,
        sms_sent_due_flag=False,
    ).select_related('booking__customer__user')  # ✅ user পর্যন্ত

    for installment in installments:
        customer = installment.booking.customer
        phone    = customer.user.phone        # ✅ fix
        name     = customer.user.full_name    # ✅ fix

        message = (
            f"প্রিয় {name}, "
            f"আজ আপনার {installment.amount} টাকার কিস্তি পরিশোধের শেষ দিন। "
            f"যোগাযোগ করুন। - Azmira"
        )

        success, error = send_sms(phone, message)

        ERPSMSLog.objects.create(
            recipient_phone = phone,
            recipient_name  = name,           # ✅ fix
            sms_type        = 'installment_due',
            message         = message,
            status          = 'sent' if success else 'failed',
            customer        = customer,
            booking         = installment.booking,
            sent_at         = timezone.now() if success else None,
            error_message   = error or '',
        )

        if success:
            installment.sms_sent_due_flag = True
            installment.save(update_fields=['sms_sent_due_flag'])