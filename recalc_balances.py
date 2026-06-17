import os
import django
import sys

# Setup Django environment
sys.path.append('d:/azmirra')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azmira.settings')
django.setup()

from mainapp.models import ERPVoucher, ERPAccountHead
from mainapp.utils.accounting import get_default_cash_account, get_default_income_account, get_default_expense_account

print("Starting recalculation script...")

# 1. Fix missing heads in Vouchers
cash = get_default_cash_account()
income = get_default_income_account()
expense = get_default_expense_account()

# Assuming empty heads mean it was an auto-generated draft for income or expense.
# We will guess based on voucher_type or amount, but since it's mostly Receipts causing this:
# Wait, for missing debit/credit on existing approved credit vouchers:
vouchers_without_heads = ERPVoucher.objects.filter(debit_head__isnull=True).exclude(status='draft')

for v in vouchers_without_heads:
    # Most of these are credit vouchers from money receipts
    if v.voucher_type == 'credit':
        v.debit_head = cash
        v.credit_head = income
        v.save(update_fields=['debit_head', 'credit_head'])
        print(f"Fixed {v.voucher_number} (Income)")
    elif v.voucher_type == 'debit':
        v.debit_head = expense
        v.credit_head = cash
        v.save(update_fields=['debit_head', 'credit_head'])
        print(f"Fixed {v.voucher_number} (Expense)")

# Also check if there are any that have credit_head as None
vouchers_without_credit_heads = ERPVoucher.objects.filter(credit_head__isnull=True).exclude(status='draft')
for v in vouchers_without_credit_heads:
    if v.voucher_type == 'credit':
        v.debit_head = cash
        v.credit_head = income
        v.save(update_fields=['debit_head', 'credit_head'])
        print(f"Fixed {v.voucher_number} (Income - credit head)")
    elif v.voucher_type == 'debit':
        v.debit_head = expense
        v.credit_head = cash
        v.save(update_fields=['debit_head', 'credit_head'])
        print(f"Fixed {v.voucher_number} (Expense - credit head)")

print("Voucher heads fixed.")

# 2. Recalculate ALL account balances from scratch
from django.db.models import Sum
from decimal import Decimal

accounts = ERPAccountHead.objects.all()
for account in accounts:
    opening = account.opening_balance
    total_debit = ERPVoucher.objects.filter(debit_head=account, status='approved').aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_credit = ERPVoucher.objects.filter(credit_head=account, status='approved').aggregate(total=Sum('amount'))['total'] or Decimal(0)

    if account.account_type in ['asset', 'expense']:
        balance = opening + total_debit - total_credit
    else:
        balance = opening + total_credit - total_debit
        
    account.current_balance = balance
    account.save(update_fields=['current_balance'])
    print(f"Recalculated {account.account_code}: {balance}")

print("Recalculation complete.")
