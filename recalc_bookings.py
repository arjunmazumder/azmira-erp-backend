import os
import django
import sys
from decimal import Decimal
from django.db.models import Sum

sys.path.append('d:/azmirra')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azmira.settings')
django.setup()

from mainapp.models import ERPBooking
from mainapp.signals import _redistribute_installments

bookings = ERPBooking.objects.all()
for booking in bookings:
    agg = booking.transactions.aggregate(total=Sum('amount'))
    total_paid = Decimal(str(agg['total'] or 0))
    total_due = booking.final_price - total_paid
    
    # Force update
    ERPBooking.objects.filter(pk=booking.id).update(
        total_paid=total_paid,
        total_due=total_due
    )
    
    booking.refresh_from_db()
    _redistribute_installments(booking)
    print(f"Booking {booking.id}: Paid={total_paid}, Due={total_due}")

print("All bookings recalculated successfully!")
