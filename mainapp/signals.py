from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

print("✅ signals.py loaded!")


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

from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mainapp.models import Transaction
from mainapp.generate_commission import create_commission_table


def _refresh_booking_totals(booking):
    transaction_total = booking.transactions.aggregate(
        total=Sum('amount')
    )['total'] or 0

    print(f"DEBUG total from DB: {transaction_total}")  # ← এই লাইন যোগ করুন

    booking.total_paid = Decimal(transaction_total)
    booking.total_due  = booking.final_price - booking.total_paid

    booking.save(update_fields=['total_paid', 'total_due', 'updated_at'])
    print(f"DEBUG after save: {booking.total_paid}, {booking.total_due}")  # ← এটাও


@receiver(post_save, sender=Transaction)
def on_transaction_saved(sender, instance, created, **kwargs):
    print("🔥 TRANSACTION SIGNAL RUNNING")

    if created:
        print(f"Transaction ID: {instance.pk}")
        create_commission_table(instance.pk)

    print(f"DEBUG booking_id: {instance.booking_id}")  # ← এই লাইন যোগ করুন

    if instance.booking_id:
        print("DEBUG: calling _refresh_booking_totals")  # ← এটাও
        _refresh_booking_totals(instance.booking)


@receiver(post_delete, sender=Transaction)
def on_transaction_deleted(sender, instance, **kwargs):
    """Transaction delete হলেও booking update হবে"""
    if instance.booking_id:
        _refresh_booking_totals(instance.booking)





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

    @receiver(post_save, sender=model, weak=False)
    def on_save(sender, instance, created, **kwargs):
        action = f'{label} {"Created" if created else "Updated"}'
        create_log(
            action=action,
            module=module,
            description=f'ID: {instance.pk} | {str(instance)[:100]}',
            log_level='info',
        )

    @receiver(post_delete, sender=model, weak=False)
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


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction, ERPMoneyReceipt

@receiver(post_save, sender=Transaction)
def create_receipt_from_transaction(sender, instance, created, **kwargs):
    if not created:
        return

    # ✅ এই check টা সরানো হয়েছে
    # if not instance.booking or not instance.customer:
    #     return

    RECEIPT_TYPE_MAP = {
        'booking_money': 'token',
        'token_money':   'token',
        'down_payment':  'down_payment',
        'installment':   'installment',
        'advance':       'other',
        'others':        'other',
    }
    receipt_type = RECEIPT_TYPE_MAP.get(instance.transaction_type, 'other')

    while True:
        last = ERPMoneyReceipt.objects.order_by('-id').first()
        if last and last.receipt_number.startswith('RCP-'):
            last_number    = int(last.receipt_number.split('-')[1])
            receipt_number = f'RCP-{str(last_number + 1).zfill(4)}'
        else:
            receipt_number = 'RCP-0001'

        if not ERPMoneyReceipt.objects.filter(receipt_number=receipt_number).exists():
            break

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