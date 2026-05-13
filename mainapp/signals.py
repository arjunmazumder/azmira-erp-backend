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

        _add_role(instance.user, 'marketing_officer')

        if instance.rank in manager_ranks:
            _add_role(instance.user, 'marketing_manager')
        else:
            _remove_role(instance.user, 'marketing_manager')

        _get_or_create_wallet_safe(instance.user, 'marketing')

    else:
        _remove_role(instance.user, 'marketing_officer')
        _remove_role(instance.user, 'marketing_manager')


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

    if instance.user is None:
        return

    if instance.is_active:
        _add_role(instance.user, 'customer')
        _get_or_create_wallet_safe(instance.user, 'customer')
    else:
        _remove_role(instance.user, 'customer')


@receiver(post_delete, sender='mainapp.ERPCustomer')
def customer_post_delete(sender, instance, **kwargs):

    if instance.user is None:
        return

    _remove_role(instance.user, 'customer')