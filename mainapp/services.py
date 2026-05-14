

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

def generate_commission(booking, amount, source_type):
    from .models import ERPCommissionRule, ERPCommission

    officer = booking.marketing_officer
    generation = 1

    while officer and generation <= 10:

        rule = ERPCommissionRule.objects.filter(
            project=booking.project,
            source_type=source_type,
            generation=generation,
            is_active=True
        ).first()

        if not rule:
            break

        commission_amount = (amount * rule.percentage) / 100

        ERPCommission.objects.create(
            marketing_officer=officer,
            booking=booking,
            source_type=source_type,
            generation=generation,
            commission_rate=rule.percentage,
            base_amount=amount,
            commission_amount=commission_amount,
            status='pending'
        )

        officer = getattr(officer, 'parent_officer', None)
        generation += 1


# api/services.py
# =====================================================
# COMMISSION SERVICE — মূল কমিশন লজিক এখানে
# =====================================================


def get_upline_chain(marketing_officer, max_levels=7):
    """
    একজন officer এর upline chain বের করে।
    
    উদাহরণ:
        A → B → C → D (A direct, B=Gen2, C=Gen3, D=Gen4)
    
    Return: [(officer, generation), ...]
        generation 0 = Direct (Shaki)
        generation 1 = 1st
        generation 2 = 2nd ... এভাবে
    """
    chain = []

    # Gen 0 = Direct Officer নিজেই (Shaki/Direct)
    chain.append((marketing_officer, 0))

    # Gen 1, 2, 3... = upline দের chain
    current = marketing_officer.upline
    generation = 1

    while current and generation <= max_levels:
        chain.append((current, generation))
        current = current.upline
        generation += 1

    return chain


@transaction.atomic
def generate_commission(booking, amount, source_type, receipt=None):
    """
    একটি payment হলে এই function call করুন।
    
    Parameters:
        booking     : ERPBooking instance
        amount      : যত টাকা payment হয়েছে (int বা Decimal)
        source_type : 'booking' / 'installment' / 'down_payment' /
                      'investment' / 'registration' / 'land_dev' /
                      'parking' / 'transfer' / 'utility'
        receipt     : ERPMoneyReceipt instance (optional, wallet transaction এ link হবে)
    
    কাজের ধাপ:
        1. Booking এর marketing officer বের করা
        2. তার upline chain বের করা (Gen 0 থেকে Gen 7)
        3. প্রতি generation এর জন্য CommissionRule খোঁজা
        4. Commission তৈরি করা
        5. Wallet এ টাকা credit করা
    """

    # ---- লেট ইমপোর্ট (circular import এড়াতে) ----
    from mainapp.models import (
        ERPCommissionRule,
        ERPCommission,
        ERPWallet,
        ERPWalletTransaction,
    )

    # ---- Step 1: Marketing Officer চেক ----
    if not booking.marketing_officer:
        # কোনো officer নেই, commission দেওয়ার কেউ নেই
        return []

    paid_amount = Decimal(str(amount))

    if paid_amount <= 0:
        return []

    project = booking.project

    # ---- Step 2: Upline Chain বের করা ----
    # chain = [(officer_obj, generation_int), ...]
    # generation 0 = Direct (নিজে), 1 = তার upline, 2 = তার upline এর upline
    chain = get_upline_chain(booking.marketing_officer, max_levels=10)

    created_commissions = []

    # ---- Step 3 & 4: প্রতি generation এ commission তৈরি ----
    for officer, generation in chain:

        # এই project + source_type + generation এর জন্য rule আছে কিনা?
        try:
            rule = ERPCommissionRule.objects.get(
                project=project,
                source_type=source_type,
                generation=generation,
                is_active=True,
            )
        except ERPCommissionRule.DoesNotExist:
            # এই generation এর জন্য rule নেই, skip করুন
            continue

        # Commission পরিমাণ হিসাব
        # percentage মানে হলো 25 মানে 25%, তাই /100 করতে হবে
        commission_amount = paid_amount * (rule.percentage / Decimal('100'))

        if commission_amount <= 0:
            continue

        # ERPCommission তৈরি করা
        commission = ERPCommission.objects.create(
            marketing_officer=officer,
            booking=booking,
            source_type=source_type,
            generation=generation,
            commission_rate=rule.percentage,
            base_amount=paid_amount,
            commission_amount=commission_amount,
            status='approved',   # সরাসরি approved করা হচ্ছে
            wallet_hit=False,
        )

        # ---- Step 5: Wallet এ টাকা Credit করা ----
        _credit_to_wallet(
            user=officer.user,
            commission=commission,
            booking=booking,
            receipt=receipt,
        )

        created_commissions.append(commission)

    return created_commissions


def _credit_to_wallet(user, commission, booking, receipt=None):
    """
    Officer এর wallet এ commission amount credit করা।
    Wallet না থাকলে তৈরি করা।
    """
    from mainapp.models import ERPWallet, ERPWalletTransaction

    # Wallet খোঁজা অথবা তৈরি করা
    wallet, created = ERPWallet.objects.get_or_create(
        user=user,
        defaults={
            'wallet_type': 'marketing',
            'balance': Decimal('0.00'),
        }
    )

    # Balance আগে কত ছিল রেকর্ড রাখা
    balance_before = wallet.balance

    # Balance বাড়ানো
    wallet.balance += commission.commission_amount
    wallet.save()

    # Transaction log তৈরি করা
    gen_label = "Direct" if commission.generation == 0 else f"Gen {commission.generation}"
    ERPWalletTransaction.objects.create(
        wallet=wallet,
        transaction_type='commission',
        amount=commission.commission_amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        booking=booking,
        receipt=receipt,
        description=(
            f"{gen_label} Commission | "
            f"Source: {commission.source_type} | "
            f"Booking: {booking.booking_code} | "
            f"Rate: {commission.commission_rate}%"
        ),
        status='paid',
        created_by='system',
    )

    # Commission এ wallet_hit আপডেট করা
    commission.wallet_hit = True
    commission.wallet_hit_at = timezone.now()
    commission.status = 'paid'
    commission.save()