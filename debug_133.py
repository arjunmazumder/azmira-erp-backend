import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azmira.settings')
django.setup()
from mainapp.models import Transaction, ERPInstallmentPlan

t = Transaction.objects.get(id=133)
print("Transaction 133 Amount:", t.amount)
print("Type:", t.transaction_type)
if t.booking:
    installments = ERPInstallmentPlan.objects.filter(booking=t.booking).order_by('id')
    for i in installments:
        print(f"Inst {i.installment_number}: Amount: {i.amount}, Due: {i.due_amount}")
