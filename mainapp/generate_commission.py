from mainapp.hierarch import define_hierarchy
from mainapp.models import Transaction, Commission, Percentage
from decimal import Decimal


def get_percentage(transaction_type):
    try:
        p = Percentage.objects.get(transaction_type=transaction_type)
        return {
            0: Decimal(str(p.gen_0)),
            1: Decimal(str(p.gen_1)),
            2: Decimal(str(p.gen_2)),
            3: Decimal(str(p.gen_3)),
            4: Decimal(str(p.gen_4)),
            5: Decimal(str(p.gen_5)),
            6: Decimal(str(p.gen_6)),
            7: Decimal(str(p.gen_7)),
        }
    except Percentage.DoesNotExist:
        print(f"No percentage config found for type: {transaction_type}")
        return {}


def commission(amount, referred_by, transaction_type):
    print("i am in commission")
    upline = define_hierarchy(referred_by)
    percentage = get_percentage(transaction_type)

    com_data = []
    for index, user_id in enumerate(upline):
        percent = percentage.get(index, Decimal('0'))
        commission_amount = (amount * percent) / Decimal('100')
        com_data.append({
            "user_id": user_id,
            "level": index,
            "percentage": percent,
            "commission": commission_amount
        })

    for item in com_data:
        print(
            f"User: {item['user_id']} | "
            f"Level: {item['level']} | "
            f"Percent: {item['percentage']}% | "
            f"Commission: {item['commission']}"
        )

    return com_data


def create_commission_table(pk):
    print("i am in create commission table")
    try:
        transaction = Transaction.objects.get(pk=pk)
        print(transaction)
    except Transaction.DoesNotExist:
        print("Transaction not found")
        return None

    if not transaction.referred_by:
        print("No referred_by — commission skipped")
        return None

    com_data = commission(
        transaction.amount,
        transaction.referred_by.id,
        transaction.transaction_type,
    )

    for item in com_data:
        print(item)
        Commission.objects.create(
            user_id=item["user_id"],
            project=transaction.project,
            plot=transaction.plot,
            level=item["level"],
            percent=item["percentage"],
            commission=item["commission"],
            commission_type=transaction.transaction_type
        )

    print(f"Done! {len(com_data)} commission records created.")
    return com_data