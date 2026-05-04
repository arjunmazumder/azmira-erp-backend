from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from datetime import datetime

def generate_money_receipt_pdf(receipt_obj):
    # আপনার ইনস্ট্রাকশন অনুযায়ী 'Amount in Words' ফরম্যাটিং (যদি মডেলে না থাকে)
    # এখানে একটি সিম্পল এক্সাম্পল দেওয়া হলো, আপনি num2words লাইব্রেরিও ব্যবহার করতে পারেন
    amount_in_words = f"BDT: {receipt_obj.amount} Taka Only." # এটি ডাইনামিক করতে হবে

    context = {
        'receipt': receipt_obj,
        'amount_in_words': amount_in_words,
        'generated_at': datetime.now().strftime("%d-%m-%Y %H:%M %p"),
    }

    # HTML টেম্পলেটকে স্ট্রিংয়ে রূপান্তর (Template ফাইলটি নিচে দেওয়া আছে)
    html_string = render_to_string('pdf/money_receipt.html', context)
    
    # PDF তৈরি
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    return pdf
