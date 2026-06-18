from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from mainapp.models import ERPMoneyReceipt, ERPVoucher, ERPSMSLog

class Command(BaseCommand):
    help = 'Check upcoming cheque deposits and send notifications/SMS'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        target_date = today + timedelta(days=2) # 2 days before

        # 1. Check Incoming Cheques (ERPMoneyReceipt)
        incoming_cheques = ERPMoneyReceipt.objects.filter(
            payment_mode='cheque',
            cheque_cleared=False,
            cheque_notification_sent=False,
            cheque_deposit_date__lte=target_date,
            cheque_deposit_date__gte=today
        )

        for receipt in incoming_cheques:
            customer_name = receipt.customer.user.full_name if (receipt.customer and receipt.customer.user) else 'Customer'
            customer_phone = receipt.customer.user.phone if (receipt.customer and receipt.customer.user) else ''
            
            message = f"Cheque Deposit Reminder: Cheque No {receipt.cheque_number} from {customer_name} is due for deposit on {receipt.cheque_deposit_date}."
            
            ERPSMSLog.objects.create(
                phone_number=customer_phone,
                message=message,
                sms_type='cheque_deposit',
                status='pending'
            )
            receipt.cheque_notification_sent = True
            receipt.save(update_fields=['cheque_notification_sent'])
            self.stdout.write(self.style.SUCCESS(f"Generated notification for incoming cheque {receipt.cheque_number}"))

        # 2. Check Outgoing Cheques (ERPVoucher)
        outgoing_cheques = ERPVoucher.objects.filter(
            payment_mode='cheque',
            cheque_cleared=False,
            cheque_notification_sent=False,
            cheque_deposit_date__lte=target_date,
            cheque_deposit_date__gte=today
        )

        for voucher in outgoing_cheques:
            message = f"Outgoing Cheque Reminder: Cheque No {voucher.cheque_number} for {voucher.amount} BDT is due to be deposited on {voucher.cheque_deposit_date}."
            
            ERPSMSLog.objects.create(
                phone_number='Admin', # Configurable admin number
                message=message,
                sms_type='admin_notification',
                status='pending'
            )
            voucher.cheque_notification_sent = True
            voucher.save(update_fields=['cheque_notification_sent'])
            self.stdout.write(self.style.SUCCESS(f"Generated notification for outgoing cheque {voucher.cheque_number}"))

        self.stdout.write(self.style.SUCCESS('Successfully processed upcoming cheque deposits.'))
