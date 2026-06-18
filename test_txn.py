import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azmira.settings')
django.setup()
from mainapp.models import Transaction, ERPCustomer, Project, Property
from decimal import Decimal

# Create a test transaction
customer = ERPCustomer.objects.first()
project = Project.objects.first()
plot = Property.objects.first()

t = Transaction.objects.create(
    transaction_type='down_payment',
    customer=customer,
    project=project,
    plot=plot,
    amount=Decimal('5000.00'),
    notes='Test API'
)

t.refresh_from_db()
print("After save, amount is:", t.amount)

