import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import ERPHoliday  # আপনার মডেলের পাথ ঠিক আছে কিনা নিশ্চিত করুন

class Command(BaseCommand):
    help = 'bangladesh_holidays_2026.csv ফাইল থেকে ২০২৬ সালের সরকারি ছুটির তালিকা ডাটাবেজে ইনসার্ট করে'

    def handle(self, *args, **kwargs):
        # CSV ফাইলের পাথ নির্ধারণ (প্রোজেক্টের মেইন ডিরেক্টরিতে ফাইলটি থাকতে হবে)
        csv_file_path = os.path.join(settings.BASE_DIR, 'bangladesh_holidays_2026.csv')

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'❌ ফাইলটি এই পাথে পাওয়া যায়নি: {csv_file_path}'))
            return

        self.stdout.write('📅 Holidays data loading শুরু হচ্ছে...\n')

        created_count = 0
        existing_count = 0

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    date_str = row.get('date')
                    name_str = row.get('name')
                    # আপনার মডেলে যদি holiday_type বা শুধু type রাখার ফিল্ড থাকে, তবে row.get('type') ব্যবহার করতে পারেন
                    
                    if not date_str or not name_str:
                        continue
                        
                    # 'YYYY-MM-DD' স্ট্রিং ডেটকে পাইথন ডেট অবজেক্টে কনভার্ট করা
                    holiday_date = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()

                    # get_or_create ব্যবহার করে ডুপ্লিকেট এড়ানো
                    holiday, created = ERPHoliday.objects.get_or_create(
                        date=holiday_date,
                        defaults={
                            'name': name_str.strip(),
                            'is_active': True
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        existing_count += 1

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️ রো (Row) প্রসেস করতে সমস্যা: {row} | এরর: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Summary:\n'
            f'  ✅ {created_count} টি নতুন ছুটি সফলভাবে ডাটাবেজে যোগ হয়েছে।\n'
            f'  ✨ {existing_count} টি ছুটি আগে থেকেই ডাটাবেজে ছিল।'
        ))