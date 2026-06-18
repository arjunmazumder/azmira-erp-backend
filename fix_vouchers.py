import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azmira.settings')
django.setup()

from mainapp.models import ERPVoucher

vouchers = ERPVoucher.objects.all()
fixed = 0
for v in vouchers:
    if v.debit_head and v.credit_head:
        # For Expense vouchers: Debit should be the Expense account
        if v.voucher_type == 'debit':
            if v.credit_head.account_type == 'expense' and v.debit_head.account_type != 'expense':
                # Swap them
                temp = v.debit_head
                v.debit_head = v.credit_head
                v.credit_head = temp
                v.save()
                print(f"Fixed Expense Voucher: {v.voucher_number} (Swapped DR/CR)")
                fixed += 1
        
        # For Income vouchers: Credit should be the Income account
        elif v.voucher_type == 'credit':
            if v.debit_head.account_type == 'income' and v.credit_head.account_type != 'income':
                # Swap them
                temp = v.debit_head
                v.debit_head = v.credit_head
                v.credit_head = temp
                v.save()
                print(f"Fixed Income Voucher: {v.voucher_number} (Swapped DR/CR)")
                fixed += 1

print(f"Total fixed: {fixed}")
