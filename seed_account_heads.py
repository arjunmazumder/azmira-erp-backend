import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azmira.settings')
django.setup()

from mainapp.models import ERPAccountHead

heads_to_create = [
    # ASSETS
    {'code': 'AST-0001', 'name': 'Cash in Hand', 'type': 'asset'},
    {'code': 'AST-0002', 'name': 'City Bank (Main Account)', 'type': 'asset'},
    {'code': 'AST-0003', 'name': 'Dutch-Bangla Bank (DBBL)', 'type': 'asset'},
    {'code': 'AST-0004', 'name': 'Cheques in Hand', 'type': 'asset'},
    {'code': 'AST-0005', 'name': 'Accounts Receivable (Customers)', 'type': 'asset'},
    {'code': 'AST-0006', 'name': 'Land & Property Assets', 'type': 'asset'},
    {'code': 'AST-0007', 'name': 'Office Equipment & Furniture', 'type': 'asset'},

    # LIABILITIES
    {'code': 'LIA-0001', 'name': 'Accounts Payable (Suppliers/Landowners)', 'type': 'liability'},
    {'code': 'LIA-0002', 'name': 'Bank Loan (Long Term)', 'type': 'liability'},
    {'code': 'LIA-0003', 'name': 'Advance from Customers', 'type': 'liability'},
    {'code': 'LIA-0004', 'name': 'Salary Payable', 'type': 'liability'},

    # INCOME
    {'code': 'INC-0001', 'name': 'Plot/Flat Sales Revenue', 'type': 'income'},
    {'code': 'INC-0002', 'name': 'Registration & Utility Fees', 'type': 'income'},
    {'code': 'INC-0003', 'name': 'Transfer Fees Income', 'type': 'income'},
    {'code': 'INC-0004', 'name': 'Other Operating Income', 'type': 'income'},

    # EXPENSE
    {'code': 'EXP-0001', 'name': 'Land Acquisition Cost', 'type': 'expense'},
    {'code': 'EXP-0002', 'name': 'Land Development & Earth Filling', 'type': 'expense'},
    {'code': 'EXP-0003', 'name': 'Construction Materials', 'type': 'expense'},
    {'code': 'EXP-0004', 'name': 'Employee Salary & Wages', 'type': 'expense'},
    {'code': 'EXP-0005', 'name': 'Sales Commission', 'type': 'expense'},
    {'code': 'EXP-0006', 'name': 'Marketing & Advertising', 'type': 'expense'},
    {'code': 'EXP-0007', 'name': 'Office Rent', 'type': 'expense'},
    {'code': 'EXP-0008', 'name': 'Utility Bills (Electricity/Internet)', 'type': 'expense'},
    {'code': 'EXP-0009', 'name': 'Conveyance & Travel', 'type': 'expense'},
    {'code': 'EXP-0010', 'name': 'Entertainment & Hospitality', 'type': 'expense'},
    {'code': 'EXP-0011', 'name': 'Legal & Govt. Fees', 'type': 'expense'},
]

created_count = 0
for head in heads_to_create:
    obj, created = ERPAccountHead.objects.get_or_create(
        account_code=head['code'],
        defaults={
            'account_name': head['name'],
            'account_type': head['type'],
        }
    )
    if created:
        created_count += 1
        print(f"Created: {obj.account_name} ({obj.account_type.upper()})")

print(f"\nSuccessfully seeded {created_count} new account heads.")
