# mainapp/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _get_or_create_wallet_safe(user, wallet_type):
    """
    UNIQUE constraint safe wallet create।
    get_or_create এর বদলে filter().first() ব্যবহার করা হয়েছে
    কারণ get_or_create race condition এ UNIQUE error দেয়।
    """
    from mainapp.models import ERPWallet

    if user is None:
        return None

    wallet = ERPWallet.objects.filter(user=user).first()

    if wallet:
        # আগে থেকে আছে — wallet_type মিলছে না হলে update করো
        if wallet.wallet_type != wallet_type:
            wallet.wallet_type = wallet_type
            wallet.save(update_fields=['wallet_type'])
        return wallet

    # নেই — create করো
    try:
        return ERPWallet.objects.create(
            user=user,
            wallet_type=wallet_type,
            balance=0,
            loan_balance=0,
        )
    except Exception:
        # Race condition — অন্য কেউ ইতিমধ্যে create করে ফেলেছে
        return ERPWallet.objects.filter(user=user).first()


def _add_role(user, role):
    """User এর roles list-এ role যোগ করো (duplicate ছাড়া)।"""
    if user is None:
        return
    roles = list(user.roles) if isinstance(user.roles, list) else []
    if role not in roles:
        roles.append(role)
        user.roles = roles
        user.save(update_fields=['roles'])


def _remove_role(user, role):
    """User এর roles list থেকে role সরাও।"""
    if user is None:
        return
    roles = list(user.roles) if isinstance(user.roles, list) else []
    if role in roles:
        roles.remove(role)
        user.roles = roles
        user.save(update_fields=['roles'])


def _sync_flags(user):
    """
    is_customer, is_investor, is_marketing flags
    roles list দেখে sync করো।
    """
    if user is None:
        return
    roles = list(user.roles) if isinstance(user.roles, list) else []
    user.is_marketing = 'marketing_officer' in roles or 'marketing_manager' in roles
    user.is_investor  = 'investor' in roles
    user.is_customer  = 'customer' in roles
    user.save(update_fields=['is_marketing', 'is_investor', 'is_customer'])


def _determine_wallet_type(user):
    """
    roles দেখে সঠিক wallet_type ঠিক করো।
    Priority: investor > customer_care > marketing (default)
    """
    roles = list(user.roles) if isinstance(user.roles, list) else []
    if 'investor' in roles:
        return 'investor'
    if 'customer_care' in roles:
        return 'customer_care'
    return 'marketing'


# =====================================================
# USER SIGNAL — নতুন User তৈরিতে auto Wallet
# =====================================================

@receiver(post_save, sender='mainapp.ERPUser')
def auto_create_wallet_on_user_save(sender, instance, created, **kwargs):
    """
    নতুন ERPUser তৈরি হলে auto wallet তৈরি।
    Wallet type roles দেখে নির্ধারিত হয়।

    investor       → wallet_type = 'investor'
    customer_care  → wallet_type = 'customer_care'
    বাকি সব        → wallet_type = 'marketing'
    """
    # Customer এর wallet দরকার নেই
    roles = list(instance.roles) if isinstance(instance.roles, list) else []
    if roles == ['customer'] or roles == []:
        return

    wallet_type = _determine_wallet_type(instance)
    _get_or_create_wallet_safe(instance, wallet_type)


# =====================================================
# EMPLOYEE SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPEmployee')
def employee_post_save(sender, instance, created, **kwargs):
    """
    ERPEmployee create/update হলে:
    - user.roles এ 'hr' যোগ করো
    - is_active=False হলে 'hr' সরাও
    """
    if instance.user is None:
        return

    if instance.is_active:
        _add_role(instance.user, 'employee')
    else:
        _remove_role(instance.user, 'employee')

    _sync_flags(instance.user)


@receiver(post_delete, sender='mainapp.ERPEmployee')
def employee_post_delete(sender, instance, **kwargs):
    """ERPEmployee delete হলে user থেকে 'hr' role সরাও।"""
    if instance.user is None:
        return
    _remove_role(instance.user, 'employee')
    _sync_flags(instance.user)


# =====================================================
# INVESTOR SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPInvestor')
def investor_post_save(sender, instance, created, **kwargs):
    """
    ERPInvestor create/update হলে:
    - user.roles এ 'investor' যোগ করো
    - investor wallet তৈরি করো (safe ভাবে)
    - is_active=False হলে 'investor' সরাও
    """
    if instance.user is None:
        return

    if instance.is_active:
        _add_role(instance.user, 'investor')
        _get_or_create_wallet_safe(instance.user, 'investor')
    else:
        _remove_role(instance.user, 'investor')

    _sync_flags(instance.user)


@receiver(post_delete, sender='mainapp.ERPInvestor')
def investor_post_delete(sender, instance, **kwargs):
    """ERPInvestor delete হলে user থেকে 'investor' role সরাও।"""
    if instance.user is None:
        return
    _remove_role(instance.user, 'investor')
    _sync_flags(instance.user)


# =====================================================
# MARKETING OFFICER SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPMarketingOfficer')
def marketing_officer_post_save(sender, instance, created, **kwargs):
    """
    ERPMarketingOfficer create/update হলে:
    - user.roles এ 'marketing_officer' যোগ করো
    - rank manager+ হলে 'marketing_manager' ও যোগ করো
    - marketing wallet তৈরি করো (safe ভাবে)
    - is_active=False হলে উভয় role সরাও
    """
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

    _sync_flags(instance.user)


@receiver(post_delete, sender='mainapp.ERPMarketingOfficer')
def marketing_officer_post_delete(sender, instance, **kwargs):
    """ERPMarketingOfficer delete হলে user থেকে marketing roles সরাও।"""
    if instance.user is None:
        return
    _remove_role(instance.user, 'marketing_officer')
    _remove_role(instance.user, 'marketing_manager')
    _sync_flags(instance.user)
