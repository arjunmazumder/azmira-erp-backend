from mainapp.hierarch import define_hierarchy


percentage = {
    0: 25,
    1: 15,
    2: 10,
    3: 7,
    4: 5,
    5: 3,
    6: 2.5,
    7: 1
}



def commission(amount, referred_by):
    upline=define_hierarchy(referred_by)
    com_data = []
    for index, user_id in enumerate(upline):
        percent = percentage.get(index, 0)
        commission_amount = (amount * percent) / 100
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

from mainapp.models import Transaction,Commission

def create_commission_table(pk):

    try:
        transaction = Transaction.objects.get(pk=pk)
        print(transaction)

    except Transaction.DoesNotExist:
        print("Transaction not found")
        return None
    
    com_data = commission(transaction.amount, transaction.referred_by.id)

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

    


