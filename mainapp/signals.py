from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

print("✅ signals.py loaded!")


# =====================================================
# HELPERS
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
# WALLET
# =====================================================

def _determine_wallet_type(user):

    roles = _get_roles(user)

    if 'investor' in roles:
        return 'investor'

    if 'customer_care' in roles:
        return 'customer_care'

    return 'marketing'


def _get_or_create_wallet_safe(user, wallet_type):

    from mainapp.models import ERPWallet

    if user is None:
        return None

    wallet = ERPWallet.objects.filter(user=user).first()

    if wallet:

        if wallet.wallet_type != wallet_type:

            wallet.wallet_type = wallet_type

            wallet.save(update_fields=['wallet_type'])

        return wallet

    try:

        return ERPWallet.objects.create(
            user=user,
            wallet_type=wallet_type,
            balance=0,
            loan_balance=0,
        )

    except Exception:

        return ERPWallet.objects.filter(user=user).first()


# =====================================================
# USER SIGNAL
# =====================================================

@receiver(post_save, sender='mainapp.ERPUser')
def auto_create_wallet_on_user_save(sender, instance, created, **kwargs):

    wallet_type = _determine_wallet_type(instance)

    _get_or_create_wallet_safe(instance, wallet_type)


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

        _get_or_create_wallet_safe(
            instance.user,
            'investor'
        )

    else:

        _remove_role(instance.user, 'investor')


@receiver(post_delete, sender='mainapp.ERPInvestor')
def investor_post_delete(sender, instance, **kwargs):

    if instance.user is None:
        return

    _remove_role(instance.user, 'investor')


# =====================================================
# MARKETING SIGNALS
# =====================================================

@receiver(post_save, sender='mainapp.ERPMarketingOfficer')
def marketing_officer_post_save(
    sender,
    instance,
    created,
    **kwargs
):

    if instance.user is None:
        return

    manager_ranks = [
        'manager',
        'senior_manager',
        'agm',
        'dgm',
        'gm'
    ]

    if instance.is_active:

        _add_role(
            instance.user,
            'marketing_officer'
        )

        if instance.rank in manager_ranks:

            _add_role(
                instance.user,
                'marketing_manager'
            )

        else:

            _remove_role(
                instance.user,
                'marketing_manager'
            )

        _get_or_create_wallet_safe(
            instance.user,
            'marketing'
        )

    else:

        _remove_role(
            instance.user,
            'marketing_officer'
        )

        _remove_role(
            instance.user,
            'marketing_manager'
        )


@receiver(post_delete, sender='mainapp.ERPMarketingOfficer')
def marketing_officer_post_delete(
    sender,
    instance,
    **kwargs
):

    if instance.user is None:
        return

    _remove_role(
        instance.user,
        'marketing_officer'
    )

    _remove_role(
        instance.user,
        'marketing_manager'
    )


@receiver(post_save, sender='mainapp.ERPCustomer')
def customer_post_save(
    sender,
    instance,
    created,
    **kwargs
):

    if instance.user is None:
        return

    if instance.is_active:

        # Add customer role
        _add_role(
            instance.user,
            'customer'
        )

        # Optional customer wallet
        _get_or_create_wallet_safe(
            instance.user,
            'customer'
        )

    else:

        # Remove customer role
        _remove_role(
            instance.user,
            'customer'
        )


@receiver(post_delete, sender='mainapp.ERPCustomer')
def customer_post_delete(
    sender,
    instance,
    **kwargs
):

    if instance.user is None:
        return

    # Remove customer role on delete
    _remove_role(
        instance.user,
        'customer'
    )