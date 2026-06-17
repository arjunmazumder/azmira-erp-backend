from decimal import Decimal
from datetime import date
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from mainapp.models import Transaction, ERPVoucher, ERPAccountHead

def get_or_create_default_account_head(account_type, name, code):
    """Fetch an account head, create if it doesn't exist."""
    head, created = ERPAccountHead.objects.get_or_create(
        account_code=code,
        defaults={
            'account_name': name,
            'account_type': account_type,
            'is_active': True,
        }
    )
    return head

def get_default_cash_account():
    return get_or_create_default_account_head('asset', 'Cash Account', 'CASH-001')

def get_default_income_account():
    return get_or_create_default_account_head('income', 'General Income', 'INC-001')

def get_default_expense_account():
    return get_or_create_default_account_head('expense', 'General Expense', 'EXP-001')


def create_transaction_and_voucher(direction, transaction_type, amount, user=None, customer=None, booking=None, project=None, plot=None, description='', create_txn=True):
    """
    Creates a Transaction and automatically generates an approved ERPVoucher.
    direction: 'in' or 'out'
    """
    amount = Decimal(str(amount))
    
    with transaction.atomic():
        # 1. Create Transaction log (if required)
        txn = None
        if create_txn:
            txn = Transaction.objects.create(
                transaction_direction=direction,
                transaction_type=transaction_type,
                amount=amount,
                user=user,
                customer=customer,
                booking=booking,
                project=project,
                plot=plot,
                notes=description,
            )
        
        # Determine Heads based on direction
        if direction == 'in':
            # Receiving money: Debit = Cash (Asset), Credit = Income
            debit_head = get_default_cash_account()
            credit_head = get_default_income_account()
            v_type = 'credit'  # Usually receiving money is tracked via Credit Voucher
        else:
            # Spending money: Debit = Expense, Credit = Cash (Asset)
            debit_head = get_default_expense_account()
            credit_head = get_default_cash_account()
            v_type = 'debit'

        # Generate Voucher Number
        year = date.today().year
        # Fix for generating safe numbers inside transaction block:
        last = ERPVoucher.objects.select_for_update().filter(voucher_number__startswith=f'VCH-{year}-').count()
        voucher_number = f'VCH-{year}-{str(last + 1).zfill(4)}'

        # 2. Create Voucher
        voucher = ERPVoucher.objects.create(
            voucher_number=voucher_number,
            voucher_type=v_type,
            amount=amount,
            description=description,
            customer=customer,
            booking=booking,
            debit_head=debit_head,
            credit_head=credit_head,
            status='approved',
            e_sign=True,
            created_by=user,
            approved_by=user,
            approved_at=date.today()
        )

        # 3. Update Account Balances
        update_account_balances(voucher)

        return txn, voucher

def update_account_balances(voucher):
    """
    Adjusts the current_balance of the debit and credit heads for an approved voucher.
    Asset/Expense: increases with Debit, decreases with Credit
    Income/Liability/Equity: increases with Credit, decreases with Debit
    """
    if voucher.status != 'approved':
        return

    amount = voucher.amount

    # Debit side
    if voucher.debit_head:
        if voucher.debit_head.account_type in ['asset', 'expense']:
            voucher.debit_head.current_balance += amount
        else:
            voucher.debit_head.current_balance -= amount
        voucher.debit_head.save(update_fields=['current_balance'])

    # Credit side
    if voucher.credit_head:
        if voucher.credit_head.account_type in ['asset', 'expense']:
            voucher.credit_head.current_balance -= amount
        else:
            voucher.credit_head.current_balance += amount
        voucher.credit_head.save(update_fields=['current_balance'])
