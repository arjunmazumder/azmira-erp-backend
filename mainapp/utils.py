from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from datetime import datetime

def generate_money_receipt_pdf(receipt_obj):

    amount_in_words = f"BDT: {receipt_obj.amount} Taka Only." 

    context = {
        'receipt': receipt_obj,
        'amount_in_words': amount_in_words,
        'generated_at': datetime.now().strftime("%d-%m-%Y %H:%M %p"),
    }

   
    html_string = render_to_string('pdf/money_receipt.html', context)
    
    # PDF তৈরি
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    return pdf
