# mainapp/signals.py
# =====================================================
# SIGNALS — ERPUser তৈরি হলে স্বয়ংক্রিয় Wallet তৈরি
# =====================================================

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='mainapp.ERPUser')
def auto_create_wallet_on_user_create(sender, instance, created, **kwargs):
    """
    যখনই একটি নতুন ERPUser তৈরি হয়, তার জন্য
    স্বয়ংক্রিয়ভাবে একটি ERPWallet তৈরি হবে।

    Wallet Type নির্ধারণ:
        - roles এ 'investor'        → wallet_type = 'investor'
        - roles এ 'customer_care'   → wallet_type = 'customer_care'
        - বাকি সবার                 → wallet_type = 'marketing'
    """
    if not created:
        # শুধু নতুন user তৈরিতে কাজ করবে, update এ না
        return

    # Circular import এড়াতে ভেতরে import করা
    from mainapp.models import ERPWallet

    # roles list থেকে wallet_type ঠিক করা
    roles = instance.roles or []

    if 'investor' in roles:
        wallet_type = 'investor'
    elif 'customer_care' in roles:
        wallet_type = 'customer_care'
    else:
        # marketing_officer, marketing_manager, admin, accounts — সবার
        # জন্য default marketing wallet
        wallet_type = 'marketing'

    # get_or_create ব্যবহার করলে duplicate হবে না
    wallet, wallet_created = ERPWallet.objects.get_or_create(
        user=instance,
        defaults={
            'wallet_type': wallet_type,
            'balance': 0,
        }
    )

    if wallet_created:
        print(f"[Signal] Wallet তৈরি হয়েছে → User: {instance.username} | Type: {wallet_type}")
    else:
        print(f"[Signal] Wallet আগে থেকেই ছিল → User: {instance.username}")