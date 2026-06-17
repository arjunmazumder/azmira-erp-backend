import sys
from mainapp.utils.accounting import create_transaction_and_voucher
try:
    txn, vch = create_transaction_and_voucher('in', 'test', 500)
    print('SUCCESS', vch.debit_head_id, vch.credit_head_id)
except Exception as e:
    print('ERROR:', e)
