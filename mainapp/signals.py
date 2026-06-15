from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mainapp.models import Transaction
from mainapp.generate_commission import create_commission_table


print("signals.py loaded!")


# =====================================================
# HELPERS — ROLE MANAGEMENT
# =====================================================

def _get_roles(user):
    return list(user.roles or [])


def _save_roles(user, roles):
    user.roles = list(set(roles))
    user.save(update_fields=['roles'])


def _add_role(user, role):
    if user is None:
        return
    roles = _get_roles(user)
    if role not in roles:
        roles.append(role)
        _save_roles(user, roles)


def _remove_role(user, role):
    if user is None:
        return
    roles = _get_roles(user)
    if role in roles:
        roles.remove(role)
        _save_roles(user, roles)


# =====================================================
# HELPERS — WALLET
# =====================================================

# ERPWallet.wallet_type choices এর সাথে মিলিয়ে রাখতে হবে
ROLE_TO_WALLET_TYPE = {
    'investor':          'investor',
    'customer':          'customer',
    'customer_care':     'customer_care',
    'marketing_officer': 'marketing',
    'marketing_manager': 'marketing',
    'employee':          'employee',
    'hr':                'employee',
    'accounts':          'accounts',
    'admin':             'admin',
    'super_admin':       'admin',
}

# Priority: যদি একজন user-এর একাধিক role থাকে, কোন wallet type পাবে
WALLET_PRIORITY = [
    'investor',
    'customer',
    'marketing_officer',
    'marketing_manager',
    'customer_care',
    'accounts',
    'hr',
    'employee',
    'admin',
    'super_admin',
]


def _determine_wallet_type(user):
    """
    User এর roles দেখে সবচেয়ে উপযুক্ত wallet type বের করে।
    Priority list অনুযায়ী প্রথম match return করে।
    কোনো role না থাকলে 'general' return করে।
    """
    roles = _get_roles(user)

    for role in WALLET_PRIORITY:
        if role in roles:
            return ROLE_TO_WALLET_TYPE.get(role, 'general')

    return 'general'


def _get_or_create_wallet_safe(user, wallet_type=None):
    """
    User এর wallet আছে কিনা চেক করে।
    - থাকলে: wallet_type ভুল হলে update করে।
    - না থাকলে: নতুন create করে।
    wallet_type না দিলে _determine_wallet_type() দিয়ে বের করে।
    """
    from mainapp.models import ERPWallet

    if user is None:
        return None

    # wallet_type না দিলে auto-detect
    if wallet_type is None:
        wallet_type = _determine_wallet_type(user)

    wallet = ERPWallet.objects.filter(user=user).first()

    if wallet:
        # type ভুল থাকলে update
        if wallet.wallet_type != wallet_type:
            wallet.wallet_type = wallet_type
            wallet.save(update_fields=['wallet_type'])
        return wallet

    # নতুন wallet create
    try:
        return ERPWallet.objects.create(
            user=user,
            wallet_type=wallet_type,
            balance=0,
            loan_balance=0,
        )
    except Exception:
        # race condition হলে filter করে return
        return ERPWallet.objects.filter(user=user).first()


# =====================================================
# USER SIGNAL
# — যেকোনো ERPUser create/update হলে wallet নিশ্চিত করে
# =====================================================

@receiver(post_save, sender='mainapp.ERPUser')
def auto_create_wallet_on_user_save(sender, instance, created, **kwargs):
    """
    যেকোনো user save হলে তার role অনুযায়ী wallet তৈরি হবে।
    Role পরিবর্তন হলে wallet type-ও update হবে।
    """
    _get_or_create_wallet_safe(instance)


# =====================================================
# EMPLOYEE SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPEmployee')
def employee_post_save(sender, instance, created, **kwargs):

    print("🔥 EMPLOYEE SIGNAL RUNNING")

    if instance.user is None:
        return

    if instance.is_active:
        _add_role(instance.user, 'employee')
        _get_or_create_wallet_safe(instance.user, 'employee')
    else:
        _remove_role(instance.user, 'employee')


@receiver(post_delete, sender='mainapp.ERPEmployee')
def employee_post_delete(sender, instance, **kwargs):

    if instance.user is None:
        return

    _remove_role(instance.user, 'employee')


# =====================================================
# INVESTOR SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPInvestor')
def investor_post_save(sender, instance, created, **kwargs):

    if instance.user is None:
        return

    if instance.is_active:
        _add_role(instance.user, 'investor')
        _get_or_create_wallet_safe(instance.user, 'investor')
    else:
        _remove_role(instance.user, 'investor')


@receiver(post_delete, sender='mainapp.ERPInvestor')
def investor_post_delete(sender, instance, **kwargs):

    if instance.user is None:
        return

    _remove_role(instance.user, 'investor')


# =====================================================
# MARKETING OFFICER SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPMarketingOfficer')
def marketing_officer_post_save(sender, instance, created, **kwargs):

    if instance.user is None:
        return

    manager_ranks = ['manager', 'senior_manager', 'agm', 'dgm', 'gm']

    if instance.is_active:
        # ✅ একসাথে সব role add করো, একবার save করো
        roles = _get_roles(instance.user)

        if 'marketing_officer' not in roles:
            roles.append('marketing_officer')

        if instance.rank in manager_ranks:
            if 'marketing_manager' not in roles:
                roles.append('marketing_manager')
        else:
            if 'marketing_manager' in roles:
                roles.remove('marketing_manager')

        # ✅ একবারই save — loop এড়াতে
        instance.user.roles = list(set(roles))
        instance.user.save(update_fields=['roles'])

        _get_or_create_wallet_safe(instance.user, 'marketing')

    else:
        roles = _get_roles(instance.user)
        roles = [r for r in roles if r not in ('marketing_officer', 'marketing_manager')]
        instance.user.roles = roles
        instance.user.save(update_fields=['roles'])

        

@receiver(post_delete, sender='mainapp.ERPMarketingOfficer')
def marketing_officer_post_delete(sender, instance, **kwargs):

    if instance.user is None:
        return

    _remove_role(instance.user, 'marketing_officer')
    _remove_role(instance.user, 'marketing_manager')


# =====================================================
# CUSTOMER SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPCustomer')
def customer_post_save(sender, instance, created, **kwargs):
    print(f"🔥 CUSTOMER SIGNAL - user: {instance.user}, is_active: {instance.is_active}")

    if instance.user is None:
        print("❌ user is None, skipping")
        return

    if instance.is_active:
        _add_role(instance.user, 'customer')
        _get_or_create_wallet_safe(instance.user, 'customer')
        print(f"✅ Role added - user roles: {instance.user.roles}")
    else:
        _remove_role(instance.user, 'customer')


@receiver(post_delete, sender='mainapp.ERPCustomer')
def customer_post_delete(sender, instance, **kwargs):

    if instance.user is None:
        return

    _remove_role(instance.user, 'customer')



# =====================================================
# TRANSACTION SIGNALS
# =====================================================





def _refresh_booking_totals(booking_id: int):
    """
    Transaction table থেকে aggregate করে booking এর
    total_paid এবং total_due update করে।
    booking.save() কল করা হয় না — QuerySet.update() ব্যবহার।
    """
    try:
        booking = ERPBooking.objects.get(pk=booking_id)
    except ERPBooking.DoesNotExist:
        return

    agg = booking.transactions.aggregate(total=Sum('amount'))
    total_paid = Decimal(str(agg['total'] or 0))
    total_due  = booking.final_price - total_paid

    # booking.save() নয় — signal loop এড়ানোর জন্য
    ERPBooking.objects.filter(pk=booking_id).update(
        total_paid=total_paid,
        total_due=total_due,
    )

    # booking object refresh করে installment redistribute
    booking.refresh_from_db()
    _redistribute_installments(booking)




def _redistribute_installments(booking):
    """
    Booking এর current total_due কে unpaid installments এ
    সমানভাবে ভাগ করে।
    - শেষ installment এ rounding error absorb হবে।
    - QuerySet.update() ব্যবহার — কোনো save() loop নেই।
    """
    unpaid_qs = ERPInstallmentPlan.objects.filter(
        booking=booking,
        is_paid=False,
    )
    count = unpaid_qs.count()

    if count == 0:
        return

    total_due = booking.total_due

    if total_due <= 0:
        # সব paid হয়ে গেছে — due 0 করে দাও
        unpaid_qs.update(amount=0, due_amount=0)
        return

    # প্রতিটা installment এ সমান ভাগ
    per_inst = (total_due / count).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    # সব unpaid installment একসাথে update
    # শেষটা আলাদা করতে হবে rounding fix এর জন্য
    unpaid_ids = list(unpaid_qs.order_by('installment_number').values_list('id', flat=True))

    if not unpaid_ids:
        return

    # শেষেরটা বাদ দিয়ে বাকিগুলো update
    non_last_ids = unpaid_ids[:-1]
    last_id      = unpaid_ids[-1]

    if non_last_ids:
        ERPInstallmentPlan.objects.filter(id__in=non_last_ids).update(
            amount=per_inst,
            due_amount=per_inst,  # unpaid তাই paid_amount=0 ধরা হচ্ছে
        )

    # শেষ installment এ বাকি সব (rounding difference absorb)
    already_allocated = per_inst * len(non_last_ids)
    last_amount = total_due - already_allocated

    ERPInstallmentPlan.objects.filter(id=last_id).update(
        amount=last_amount,
        due_amount=last_amount,
    )



@receiver(post_save, sender=Transaction, weak=False, dispatch_uid="on_transaction_saved")
def on_transaction_saved(sender, instance, created, **kwargs):
    """
    Transaction save হলে:
    1. নতুন হলে commission তৈরি
    2. Booking এর total_paid/due refresh
    3. Unpaid installments redistribute
    """
    if created:
        create_commission_table(instance.pk)

    if instance.booking_id:
        _refresh_booking_totals(instance.booking_id)


@receiver(post_delete, sender=Transaction, weak=False, dispatch_uid="on_transaction_deleted")
def on_transaction_deleted(sender, instance, **kwargs):
    """
    Transaction delete হলেও booking ও installment update হবে।
    """
    if instance.booking_id:
        _refresh_booking_totals(instance.booking_id)





# mainapp/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from mainapp.log_utils import create_log

# =====================================================
# কোন model → কোন module নামে log হবে
# =====================================================
MODEL_MODULE_MAP = {
    'ERPBooking':          ('Booking',     'BOOKING'),
    'ERPCustomer':         ('Customer',    'CUSTOMER'),
    'ERPLead':             ('Lead',        'LEAD'),
    'ERPMoneyReceipt':     ('Payment',     'ACCOUNTS'),
    'ERPInstallmentPlan':  ('Installment', 'ACCOUNTS'),
    'ERPVoucher':          ('Voucher',     'ACCOUNTS'),
    'Property':            ('Property',    'PROPERTY'),
    'Project':             ('Project',     'PROJECT'),
    'ERPEmployee':         ('Employee',    'HR'),
    'ERPPayroll':          ('Payroll',     'HR'),
    'ERPAttendance':       ('Attendance',  'HR'),
    'ERPMarketingOfficer': ('Officer',     'MARKETING'),
    'ERPLead':             ('Lead',        'MARKETING'),
    'ERPInvestor':         ('Investor',    'INVESTOR'),
    'ERPInvestment':       ('Investment',  'INVESTOR'),
    'ERPDividend':         ('Dividend',    'INVESTOR'),
    'ERPLandAcquisition':  ('Land',        'LAND'),
    'ERPLandRecord':       ('Land Record', 'LAND'),
    'ERPWallet':           ('Wallet',      'WALLET'),
    'ERPWalletTransaction':('Wallet Txn',  'WALLET'),
    'ERPLoan':             ('Loan',        'HR'),
    'ERPOfficerRequest':   ('Request',     'MARKETING'),
    'ERPOffer':            ('Offer',       'MARKETING'),
    'ERPDocument':         ('Document',    'LEGAL'),
    'ERPCompanyAsset':     ('Asset',       'LOGISTICS'),
    'ERPProjectVisit':     ('Visit',       'MARKETING'),
    'Transaction':         ('Transaction', 'ACCOUNTS'),
}

# =====================================================
# যে সব model signal দেবে
# =====================================================
from mainapp.models import (
    ERPBooking, ERPCustomer, ERPLead, ERPMoneyReceipt,
    ERPInstallmentPlan, ERPVoucher, Property, Project,
    ERPEmployee, ERPPayroll, ERPAttendance, ERPMarketingOfficer,
    ERPInvestor, ERPInvestment, ERPDividend, ERPLandAcquisition,
    ERPLandRecord, ERPWallet, ERPWalletTransaction, ERPLoan,
    ERPOfficerRequest, ERPOffer, ERPDocument, ERPCompanyAsset,
    ERPProjectVisit, Transaction,
)

TRACKED_MODELS = [
    ERPBooking, ERPCustomer, ERPLead, ERPMoneyReceipt,
    ERPInstallmentPlan, ERPVoucher, Property, Project,
    ERPEmployee, ERPPayroll, ERPAttendance, ERPMarketingOfficer,
    ERPInvestor, ERPInvestment, ERPDividend, ERPLandAcquisition,
    ERPLandRecord, ERPWallet, ERPWalletTransaction, ERPLoan,
    ERPOfficerRequest, ERPOffer, ERPDocument, ERPCompanyAsset,
    ERPProjectVisit, Transaction,
]


def _make_handlers(model):
    model_name = model.__name__
    label, module = MODEL_MODULE_MAP.get(model_name, (model_name, 'SYSTEM'))

    @receiver(post_save, sender=model, weak=False, dispatch_uid=f"log_save_{model.__name__}")
    def on_save(sender, instance, created, **kwargs):
        action = f'{label} {"Created" if created else "Updated"}'
        create_log(
            action=action,
            module=module,
            description=f'ID: {instance.pk} | {str(instance)[:100]}',
            log_level='info',
        )

    @receiver(post_delete, sender=model, weak=False, dispatch_uid=f"log_delete_{model.__name__}")
    def on_delete(sender, instance, **kwargs):
        create_log(
            action=f'{label} Deleted',
            module=module,
            description=f'ID: {instance.pk} | {str(instance)[:100]}',
            log_level='warning',
        )


# সব model এ handler লাগাও
for _model in TRACKED_MODELS:
    _make_handlers(_model)


from django.db import transaction

@receiver(post_save, sender=Transaction, dispatch_uid="create_receipt_from_transaction")
def create_receipt_from_transaction(sender, instance, created, **kwargs):
    if not created:
        return

    RECEIPT_TYPE_MAP = {
        'booking_money': 'token',
        'token_money':   'token',
        'down_payment':  'down_payment',
        'installment':   'installment',
        'advance':       'other',
        'others':        'other',
    }
    receipt_type = RECEIPT_TYPE_MAP.get(instance.transaction_type, 'other')

    with transaction.atomic():
        last = ERPMoneyReceipt.objects.filter(receipt_number__startswith='RCP-').select_for_update().order_by('-id').first()
        if last:
            try:
                last_number    = int(last.receipt_number.split('-')[1])
            except ValueError:
                last_number = 0
            receipt_number = f'RCP-{str(last_number + 1).zfill(4)}'
        else:
            receipt_number = 'RCP-0001'

        ERPMoneyReceipt.objects.create(
            receipt_number = receipt_number,
            booking        = instance.booking,    # None হলেও চলবে
            customer       = instance.customer,   # None হলেও চলবে
            user           = instance.user, 
            receipt_type   = receipt_type,
            amount         = instance.amount,
            payment_date   = instance.created_at.date(),
            payment_mode   = 'cash',
            status         = 'pending',
            notes          = instance.notes or '',
        )


@receiver(post_save, sender=ERPMoneyReceipt, dispatch_uid="auto_create_voucher_for_receipt")
def auto_create_voucher_for_receipt(sender, instance, created, **kwargs):
    """
    Automatically create a draft ERPVoucher when an ERPMoneyReceipt is generated.
    """
    if created:
        with transaction.atomic():
            last = ERPVoucher.objects.filter(voucher_number__startswith='VCH-').select_for_update().order_by('-id').first()
            if last:
                try:
                    last_number = int(last.voucher_number.split('-')[1])
                except ValueError:
                    last_number = 0
                voucher_number = f'VCH-{str(last_number + 1).zfill(4)}'
            else:
                voucher_number = 'VCH-0001'

            ERPVoucher.objects.create(
                voucher_number=voucher_number,
                voucher_type='credit',
                voucher_date=instance.payment_date,
                entry_date=instance.entry_date,
                amount=instance.amount,
                description=f"Auto-generated draft voucher for Receipt #{instance.receipt_number}",
                booking=instance.booking,
                customer=instance.customer,
                status='draft'
            )


@receiver(post_save, sender=ERPWalletTransaction, dispatch_uid="update_wallet_balance")
def update_wallet_balance(sender, instance, created, **kwargs):
    """
    Safely update ERPWallet.balance when ERPWalletTransaction is approved or paid.
    Uses select_for_update() to prevent race conditions.
    """
    if instance.status in ['approved', 'paid'] and instance.amount != 0:
        # Prevent applying the same transaction multiple times
        if instance.balance_before == 0 and instance.balance_after == 0:
            with transaction.atomic():
                wallet = ERPWallet.objects.select_for_update().get(pk=instance.wallet_id)
                
                balance_before = wallet.balance
                if getattr(instance, 'transaction_direction', 'in') == 'in':
                    wallet.balance += instance.amount
                else:
                    wallet.balance -= instance.amount
                
                balance_after = wallet.balance
                wallet.save(update_fields=['balance'])
                
                # Update the transaction record with the captured balances
                ERPWalletTransaction.objects.filter(pk=instance.pk).update(
                    balance_before=balance_before,
                    balance_after=balance_after
                )