import os
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.db import models
from datetime import date, timedelta
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
import random
from django.db import models, transaction
from django.core.files.base import ContentFile




# =====================================================
# REAL ESTATE ERP - mainapp/models.py
# =====================================================


# =====================================================
# 1. USER & AUTHENTICATION************(DONE)
# =====================================================

# models.py


import os
from io import BytesIO
from PIL import Image
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# =====================================================
# USER MANAGER (Custom User তৈরির জন্য এটি জরুরি)
# =====================================================
class ERPUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)  # এটি পাসওয়ার্ডকে হ্যাশ করে সেভ করবে
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

# =====================================================
# MAIN USER MODEL
# =====================================================

class ERPUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('accounts', 'Accounts Officer'),
        ('employee', 'Employee'),
        ('marketing_officer', 'Marketing Officer'),
        ('marketing_manager', 'Marketing Manager'),
        ('customer_care', 'Customer Care'),
        ('hr', 'HR Manager'),
        ('customer', 'Customer'),
        ('investor', 'Investor'),
    ]

    DEPARTMENT_CHOICES = [
        ('management', 'Management'),
        ('accounts', 'Accounts'),
        ('marketing', 'Marketing'),
        ('customer_care', 'Customer Care'),
        ('hr', 'Human Resources'),
        ('legal', 'Legal'),
    ]

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True, default='')
    nid = models.CharField(max_length=50, blank=True, null=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='erp/users/', blank=True, null=True)
    roles = models.JSONField(default=list, blank=True, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    father_name      = models.CharField(max_length=200, blank=True, null=True, default='')
    mother_name      = models.CharField(max_length=200, blank=True, null=True, default='')
    spouse_name      = models.CharField(max_length=200, blank=True, null=True, default='')
    phone_alt        = models.CharField(max_length=20, blank=True, null=True, default='')
    present_address  = models.TextField(blank=True, null=True, default='')
    permanent_address= models.TextField(blank=True, null=True, default='')
    nid_image        = models.ImageField(upload_to='erp/customers/nid/', blank=True, null=True)
    loyalty_points   = models.IntegerField(default=0)
    notes            = models.TextField(blank=True, null=True, default='')
    objects = ERPUserManager()
    referred_by = models.ForeignKey('self',on_delete=models.SET_NULL,null=True, blank=True,related_name='referred_users')
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','full_name']

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f'{self.username} - {self.id}'

    # =====================================================
    # DYNAMIC FLAGS
    # =====================================================
    @property
    def is_customer(self):
        return 'customer' in (self.roles or [])

    @property
    def is_investor(self):
        return 'investor' in (self.roles or [])

    @property
    def is_employee(self):
        return 'employee' in (self.roles or [])

    @property
    def is_marketing(self):
        return any(
            r in (self.roles or [])
            for r in ['marketing_officer', 'marketing_manager']
        )

    # =====================================================
    # IMAGE CONVERSION (WebP)
    # =====================================================
    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                img_io = BytesIO()
                img.save(img_io, format='WEBP', quality=80)

                new_filename = os.path.splitext(self.image.name)[0] + '.webp'
                self.image.save(
                    new_filename,
                    ContentFile(img_io.getvalue()),
                    save=False
                )
            except Exception as e:
                print('Image conversion failed:', e)

        super().save(*args, **kwargs)


# =====================================================
# 2. PROJECT*************************(DONE)
# =====================================================

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('plot', 'Plot'),
        ('flat', 'Flat'),
        ('both', 'Both'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('sold_out', 'Sold Out'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    id = models.BigAutoField(primary_key=True)
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='lot')
    description = models.TextField(blank=True, null=True, default='')
    address = models.TextField(blank=True, null=True, default='')
    city = models.CharField(max_length=100, blank=True, null=True, default='')
    district = models.CharField(max_length=100, blank=True, null=True, default='')
    upazila = models.CharField(max_length=100, blank=True, null=True, default='')
    mouza = models.CharField(max_length=100, blank=True, null=True, default='')
    total_land_area = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    land_unit = models.CharField(max_length=20, default='katha')
    total_plots = models.IntegerField(default=0)
    available_plots = models.IntegerField(default=0)
    total_project_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    launch_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='erp/projects/', blank=True, null=True, default='')
    layout_image = models.ImageField(upload_to='erp/projects/layouts/', blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.project_code} - {self.project_name}'

    def save(self, *args, **kwargs):
        for field in [self.image, self.layout_image]:
            if field and hasattr(field, 'file'):
                try:
                    img = Image.open(field)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    img_io = BytesIO()
                    img.save(img_io, format='WEBP', quality=80)
                    new_filename = os.path.splitext(field.name)[0] + '.webp'
                    field.save(new_filename, ContentFile(img_io.getvalue()), save=False)
                except Exception as e:
                    print(f'Image conversion failed: {e}')
        super().save(*args, **kwargs)


# =====================================================
# 3. PLOT / FLAT ******************(DONE)
# =====================================================

class Property(models.Model):
    PLOT_TYPE_CHOICES = [
        ('plot', 'Plot'),
        ('flat', 'Flat'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
        ('hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]

    FACING_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('north_east', 'North-East'),
        ('north_west', 'North-West'),
        ('south_east', 'South-East'),
        ('south_west', 'South-West'),
    ]

    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='property')
    plot_number = models.CharField(max_length=50, blank=True, null=True)
    plot_type = models.CharField(max_length=20, choices=PLOT_TYPE_CHOICES, default='plot')
    area = models.CharField(max_length=255, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    block = models.CharField(max_length=255, blank=True, null=True)
    road = models.CharField(max_length=255, blank=True, null=True)
    floor_number = models.CharField(max_length=255, blank=True, null=True)
    floor = models.CharField(max_length=255, blank=True, null=True)
    area_unit = models.CharField(max_length=20, default='katha')
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    facing = models.CharField(max_length=20, choices=FACING_CHOICES, blank=True, null=True, default='')
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    flat_number = models.CharField(max_length=20, blank=True, null=True, default='')
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    layout_x = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    layout_y = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='properties/images/', blank=True, null=True)
    total_share = models.CharField(max_length=255, blank=True, null=True)
    building_type = models.CharField(max_length=255, blank=True, null=True)
    building_orientation = models.CharField(max_length=255, blank=True, null=True)
    unit_per_floor = models.CharField(max_length=255, blank=True, null=True)
    unit_a = models.CharField(max_length=255, blank=True, null=True)
    unit_b = models.CharField(max_length=255, blank=True, null=True)
    unit_c = models.CharField(max_length=255, blank=True, null=True)
    bedroom = models.CharField(max_length=255, blank=True, null=True)
    bathroom = models.CharField(max_length=255, blank=True, null=True)
    balcony = models.CharField(max_length=255, blank=True, null=True)
    drawing_dining_room = models.CharField(max_length=255, blank=True, null=True)
    kitchen = models.CharField(max_length=255, blank=True, null=True)
    garden = models.CharField(max_length=255, blank=True, null=True)
    lift = models.CharField(max_length=255, blank=True, null=True)
    parking = models.CharField(max_length=255, blank=True, null=True)
    hall = models.CharField(max_length=255, blank=True, null=True)
    electricity_backup = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
   

    def __str__(self):
        return f"Specification {self.id}"

    class Meta:
        unique_together = [['project', 'plot_number']]
        ordering = ['plot_number']

    def __str__(self):
        return f'{self.project.project_code} - Plot {self.plot_number}'


# =====================================================
# 4. LAND RECORD (DONE)
# =====================================================

class ERPLandRecord(models.Model):
    LAND_STATUS_CHOICES = [
        ('porcha', 'পর্চা'),
        ('khotian', 'খতিয়ান'),
        ('deed_done', 'দলিল সম্পন্ন'),
        ('baina', 'বায়না'),
        ('power_of_attorney', 'পাওয়ার অব অ্যাটর্নি'),
        ('saf_kobola', 'সাফ কবলা'),
        ('namjari', 'নামজারি'),
        ('registration_done', 'রেজিস্ট্রেশন সম্পন্ন'),
    ]

    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='land_records')
    dag_number = models.CharField(max_length=100, blank=True, null=True, default='')
    khotian_number = models.CharField(max_length=100, blank=True, null=True, default='')
    mouza = models.CharField(max_length=200, blank=True, null=True, default='')
    total_area = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    area_unit = models.CharField(max_length=20, default='katha')
    purchased_area = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    land_owner_name = models.CharField(max_length=200, blank=True, null=True, default='')
    deed_number = models.CharField(max_length=100, blank=True, null=True, default='')
    deed_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    land_status = models.CharField(max_length=30, choices=LAND_STATUS_CHOICES, default='porcha')
    registration_date = models.DateField(blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True, default='')
    namjari_done = models.BooleanField(default=True)
    namjari_date = models.DateField(blank=True, null=True)
    sub_registry_office = models.CharField(max_length=200, blank=True, null=True, default='')
    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.project.project_name} - Dag {self.dag_number}'


# =====================================================
# 5. CUSTOMER********************(DONE)
# =====================================================


class ERPCustomer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('joint', 'Joint'),
        ('corporate', 'Corporate'),
    ]

    SOURCE_CHOICES = [
        ('walk_in', 'Walk In'),
        ('referral', 'Referral'),
        ('marketing', 'Marketing Officer'),
        ('online', 'Online'),
        ('advertisement', 'Advertisement'),
        ('existing', 'Existing Customer'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
            ERPUser,
            on_delete=models.PROTECT,
            related_name='customer_profile'
        )
    customer_code = models.CharField(max_length=50, unique=True, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    source        = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='walk_in')
    created_by    = models.CharField(max_length=100, blank=True, null=True, default='')
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer_code} - {self.user.full_name if self.user else "No User"}'

    @staticmethod
    def _generate_unique_code():
        with transaction.atomic():
            last = ERPCustomer.objects.select_for_update().order_by('-id').last()
            if last and last.customer_code:
                try:
                    last_num = int(last.customer_code.split('-')[-1])
                    next_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = ERPCustomer.objects.count() + 1
            else:
                next_num = 1

            while True:
                code = f"ACL-{next_num:04d}"
                if not ERPCustomer.objects.filter(customer_code=code).exists():
                    return code
                next_num += 1

    def save(self, *args, **kwargs):
        if not self.customer_code:
            self.customer_code = self._generate_unique_code()
        super().save(*args, **kwargs)



# =====================================================
# 6. LEAD MANAGEMENT (Done)
# =====================================================

class ERPLead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('follow_up', 'Follow Up'),
        ('visit_scheduled', 'Visit Scheduled'),
        ('visited', 'Visited'),
        ('negotiating', 'Negotiating'),
        ('converted', 'Converted to Customer'),
        ('lost', 'Lost'),
        ('not_interested', 'Not Interested'),
    ]

    SOURCE_CHOICES = [
        ('walk_in', 'Walk In'),
        ('referral', 'Referral'),
        ('facebook', 'Facebook'),
        ('website', 'Website'),
        ('billboard', 'Billboard'),
        ('newspaper', 'Newspaper'),
        ('phone_call', 'Phone Call'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    lead_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=150, blank=True, null=True, default='')
    address = models.TextField(blank=True, null=True, default='')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='walk_in')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    # একটি lead একাধিক officer-এ assign করা যাবে না
    assigned_to = models.ForeignKey(
        'ERPMarketingOfficer', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads'
    )
    interested_in = models.ForeignKey(
        Project, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leads'
    )
    # Conversation log — admin monitoring করতে পারবে
    conversation_log = models.JSONField(default=list, blank=True)
    next_follow_up = models.DateTimeField(blank=True, null=True)
    last_contacted = models.DateTimeField(blank=True, null=True)
    converted_customer = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='lead_source'
    )
    converted_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.lead_code} - {self.full_name}'


#======================================================
# TRANACTIONS TABLE
#=====================================================
# models.py
class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('booking_money', 'Booking-Money'),
        ('down_payment', 'Down-payment'),
        ('installment', 'Installment'),
        ('token_money', 'Token-Money'),
        ('advance', 'Advance'),
        ('loan', 'Loan'),
        ('transfer', 'Transfer'),
        ('investment', 'Investment'),
        ('registration', 'Registration'),
        ('land_development', 'Land-Development'),
        ('parking', 'Parking'),
        ('utility', 'Utility'),
        ('others', 'Others'),
    ]

    id               = models.BigAutoField(primary_key=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE, default='booking_money')
    booking          = models.ForeignKey(
        'ERPBooking', on_delete=models.CASCADE,
        related_name='transactions', null=True, blank=True
    )
    customer         = models.ForeignKey(ERPCustomer, on_delete=models.CASCADE, related_name='customer_transactions', null=True, blank=True,)
    user             = models.ForeignKey(ERPUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_transactions')
    project          = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_transactions')
    plot             = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='plot_transactions')
    referred_by      = models.ForeignKey(
        ERPUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='referred_transactions'
    )
    amount           = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transferred_to   = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='received_transfers'
    )
    notes      = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.customer.user.full_name if self.customer and self.customer.user else 'Unknown'
        return f"{full_name} - {self.get_transaction_type_display()} ({self.amount})"


#======================================================
# COMMISSION TABLE
#=====================================================

class Commission(models.Model):

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        ERPUser,
        on_delete=models.CASCADE,
        related_name='commissions'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='commissions'
    )

    plot = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='commissions'
    )

    level = models.PositiveIntegerField(default=0)

    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    commission_type = models.CharField(
        max_length=30,
        default='sale'
    )

    note = models.TextField(
        blank=True,
        null=True,
        default=''
    )

    created_at = models.DateTimeField(auto_now_add=True)

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'commissions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.full_name} - {self.commission}'




# =====================================================
# 7. BOOKING*********************(DONE)
# =====================================================

from decimal import Decimal
from datetime import date, timedelta
from django.db import models
from django.db.models import Sum


class ERPBooking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('agreement_done', 'Agreement Done'),
        ('registration_done', 'Registration Done'),
        ('cancelled', 'Cancelled'),
        ('transferred', 'Transferred'),
    ]

    CANCEL_REASON_CHOICES = [
        ('customer_request', 'Customer Request'),
        ('token_expired', 'Token Expired'),
        ('payment_default', 'Payment Default'),
        ('other', 'Other'),
    ]

    id                = models.BigAutoField(primary_key=True)
    booking_code      = models.CharField(max_length=50, unique=True)
    customer          = models.ForeignKey(ERPCustomer, on_delete=models.CASCADE, related_name='bookings')
    plot              = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    project           = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bookings')
    marketing_officer = models.ForeignKey(
        'ERPMarketingOfficer', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='bookings'
    )
    booking_date      = models.DateField(default=date.today)
    status            = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')

    total_price      = models.DecimalField(max_digits=16, decimal_places=2)
    discount_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_note    = models.CharField(max_length=200, blank=True, null=True, default='')
    final_price      = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    token_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    token_paid_date   = models.DateField(blank=True, null=True)
    token_expiry_date = models.DateField(blank=True, null=True)
    token_status      = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('expired', 'Expired'), ('demolished', 'Demolished')],
        default='active'
    )

    down_payment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    down_payment_date   = models.DateField(blank=True, null=True)

    total_paid = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_due  = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    # Cancellation
    cancel_reason = models.CharField(max_length=30, choices=CANCEL_REASON_CHOICES, blank=True, null=True, default='')
    cancel_date   = models.DateField(blank=True, null=True)
    cancel_note   = models.TextField(blank=True, null=True, default='')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_date   = models.DateField(blank=True, null=True)
    refund_note   = models.TextField(blank=True, null=True, default='')

    # Transfer
    transferred_to          = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transferred_bookings'
    )
    transfer_date           = models.DateField(blank=True, null=True)
    transfer_service_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notes      = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.customer.user.full_name if self.customer and self.customer.user else 'Unknown'
        return f'{self.booking_code} - {full_name}'

    def calculate_token_expiry(self):
        if not self.token_paid_date or not self.token_amount:
            return None
        amount = float(self.token_amount)
        days   = 30 if amount <= 500 else 60 if amount <= 1000 else 90
        return self.token_paid_date + timedelta(days=days)

    def save(self, *args, **kwargs):
    # ১. Guard clause
        update_fields = kwargs.get('update_fields')
        if update_fields and set(update_fields) <= {'total_paid', 'total_due', 'updated_at'}:
            super().save(*args, **kwargs)
            return

        # ২. Final Price
        total         = self.total_price or 0
        discount      = self.discount_amount or 0
        self.final_price = total - discount

        # ৩. total_due — প্রথমবার total_paid=0, তাই final_price=total_due ✅
        self.total_due = self.final_price - self.total_paid

        # ৪. Token expiry
        if self.token_paid_date and self.token_amount and not self.token_expiry_date:
            self.token_expiry_date = self.calculate_token_expiry()

        super().save(*args, **kwargs)



# =====================================================
# 8. INSTALLMENT PLAN**************(DONE)
# =====================================================

class ERPInstallmentPlan(models.Model):
    id = models.BigAutoField(primary_key=True)
    booking = models.ForeignKey(
        'ERPBooking',
        on_delete=models.CASCADE,
        related_name='installment_plan'
    )
    installment_number = models.IntegerField()
    due_date = models.DateField()

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_paid = models.BooleanField(default=False)

    # 🔥 Future-ready SMS tracking (recommended)
    sms_sent_48h_flag = models.BooleanField(default=True)
    sms_sent_due_flag = models.BooleanField(default=True)

    notes = models.TextField(blank=True, null=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['installment_number']
        unique_together = [['booking', 'installment_number']]

    def __str__(self):
        return f'Installment #{self.installment_number} for {self.booking.booking_code}'

    # 🔥 Business Logic Methods (Option 2)

    def sms_sent_48h(self):
        """
        Due date এর 48 ঘন্টা আগে SMS sent condition
        """
        if self.is_paid:
            return True
        return self.due_date == date.today() + timedelta(days=2)

    sms_sent_48h.boolean = True
    sms_sent_48h.short_description = "SMS 48h"

    def sms_sent_due(self):
        """
        Due date এ SMS sent condition
        """
        if self.is_paid:
            return True
        return self.due_date == date.today()

    sms_sent_due.boolean = True
    sms_sent_due.short_description = "SMS Due"

  # 🔥 Save override (Safe calculation & Auto-update Booking)
    def save(self, *args, **kwargs):
        # ১. কিস্তির নিজস্ব ডিউ এবং পেইড স্ট্যাটাস আপডেট
        self.due_amount = (self.amount or 0) - (self.paid_amount or 0)
        self.is_paid = self.paid_amount >= self.amount
        
        # ২. কিস্তি সেভ (এটি ডাটাবেসে ডাটা পাঠাবে)
        super().save(*args, **kwargs)

        # ৩. মেইন বুকিং আপডেট (বুকিং এর save মেথড কল হবে এবং সব হিসাব নতুন করে হবে)
        if self.booking:
            self.booking.save()


# =====================================================
# 9. MONEY RECEIPT****************(DONE)
# =====================================================

class ERPMoneyReceipt(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('authorized', 'Authorized'),
        ('rejected', 'Rejected'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('mobile_banking', 'Mobile Banking (bKash/Nagad)'),
        ('online', 'Online Transfer'),
    ]

    RECEIPT_TYPE_CHOICES = [
        ('token', 'Token/Booking Money'),
        ('down_payment', 'Down Payment'),
        ('installment', 'Installment'),
        ('full_payment', 'Full Payment'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    booking = models.ForeignKey(ERPBooking, on_delete=models.CASCADE, related_name='money_receipts')
    customer = models.ForeignKey(ERPCustomer, on_delete=models.CASCADE, related_name='money_receipts')
    installment = models.ForeignKey(
        ERPInstallmentPlan, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='receipts'
    )
    receipt_type = models.CharField(max_length=20, choices=RECEIPT_TYPE_CHOICES, default='installment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=date.today)
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES, default='cash')
    bank_name = models.CharField(max_length=100, blank=True, null=True, default='')
    cheque_number = models.CharField(max_length=50, blank=True, null=True, default='')
    cheque_date = models.DateField(blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, default='')
    # Cheque 30 দিনে cash না হলে জিরো
    cheque_deposit_date = models.DateField(blank=True, null=True)
    cheque_cleared = models.BooleanField(default=True)
    cheque_cleared_date = models.DateField(blank=True, null=True)
    cheque_notification_sent = models.BooleanField(default=True)
    # 3-stage: Pending → Complete → Authorized
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by_customer = models.BooleanField(default=True)
    e_sign = models.BooleanField(default=True)
    e_sign_date = models.DateTimeField(blank=True, null=True)
    completed_by = models.CharField(max_length=100, blank=True, null=True, default='')
    completed_at = models.DateTimeField(blank=True, null=True)
    authorized_by = models.CharField(max_length=100, blank=True, null=True, default='')
    authorized_at = models.DateTimeField(blank=True, null=True)
    # Backdated entry নেই
    entry_date = models.DateField(default=date.today)
    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Receipt #{self.receipt_number} - {self.customer.full_name}'


# =====================================================
# 10. VOUCHER (DONE)
# =====================================================
class ERPVoucher(models.Model):
    VOUCHER_TYPE_CHOICES = [
        ('debit', 'Debit Voucher'),
        ('credit', 'Credit Voucher'),
        ('journal', 'Journal Voucher'),
        ('contra', 'Contra Voucher'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.BigAutoField(primary_key=True)
    voucher_number = models.CharField(max_length=50, unique=True)
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES)
    voucher_date = models.DateField(default=date.today)
    entry_date = models.DateField(default=date.today)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True, default='')
    booking = models.ForeignKey(
        ERPBooking, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='vouchers'
    )
    customer = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='vouchers'
    )
    debit_head = models.ForeignKey(
        "ERPAccountHead", on_delete=models.SET_NULL,
        null=True, blank=True, related_name='debit_vouchers'
    )
    credit_head = models.ForeignKey(
       "ERPAccountHead", on_delete=models.SET_NULL,
        null=True, blank=True, related_name='credit_vouchers'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    e_sign = models.BooleanField(default=False)

    approved_by = models.ForeignKey(
        ERPUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_vouchers'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        ERPUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_vouchers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.voucher_number} - {self.voucher_type}'
    

# =====================================================
# 11. PROJECT VISIT (DONE)
# =====================================================
class ERPProjectVisit(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    id = models.BigAutoField(primary_key=True)

    # ✅ CASCADE → PROTECT
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='visits'
    )
    customer = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='visits'
    )
    lead = models.ForeignKey(
        ERPLead, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='visits'
    )
    guest_name = models.CharField(max_length=200, blank=True, null=True, default='')
    guest_phone = models.CharField(max_length=20, blank=True, null=True, default='')
    visit_date = models.DateTimeField()
    marketing_officer = models.ForeignKey(
        'ERPMarketingOfficer', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='arranged_visits'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # ✅ CharField → FK
    confirmed_by = models.ForeignKey(
        'ERPUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='confirmed_visits'
    )
    confirmed_at = models.DateTimeField(blank=True, null=True)
    outcome = models.TextField(blank=True, null=True, default='')

    # ✅ default=False — visit হওয়ার আগে interested জানার প্রশ্নই নেই
    interested = models.BooleanField(default=False)

    # ✅ default=False — নতুন visit এ notification যায়নি
    notification_sent_24h = models.BooleanField(default=False)
    notification_sent_2h  = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f'Visit - {self.project.project_name} - {self.visit_date}'
    

# =====================================================
# 12. MARKETING OFFICER (DONE)
# =====================================================

class ERPMarketingOfficer(models.Model):
    RANK_CHOICES = [
        ('officer', 'Marketing Officer'),
        ('senior_officer', 'Senior Officer'),
        ('team_leader', 'Team Leader'),
        ('assistant_manager', 'Assistant Manager'),
        ('manager', 'Manager'),
        ('senior_manager', 'Senior Manager'),
        ('agm', 'AGM'),
        ('dgm', 'DGM'),
        ('gm', 'GM'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(ERPUser, on_delete=models.CASCADE, related_name='marketing_profile')
    officer_code = models.CharField(max_length=50, unique=True)
    rank = models.CharField(max_length=30, choices=RANK_CHOICES, default='officer')
    rank_achieved_at = models.DateTimeField(blank=True, null=True)
    upline = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='downline'
    )
    joining_date = models.DateField(blank=True, null=True)
    target_sales = models.IntegerField(default=0)
    commission_rate_lot = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    commission_rate_flat = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.officer_code} - {self.user.full_name} ({self.rank})'


# =====================================================
# 13. WALLET (DONE)
# =====================================================

class ERPWallet(models.Model):
    WALLET_TYPE_CHOICES = [
        ('marketing','Marketing Officer Wallet'),
        ('investor','Investor Wallet'),
        ('customer','Customer Wallet'),
        ('customer_care','Customer Care Wallet'),
        ('employee','Employee Wallet'),
        ('accounts','Accounts Officer Wallet'),
        ('admin','Admin Wallet'),
        ('general','General Wallet'),    
    ]

    id= models.BigAutoField(primary_key=True)
    user= models.OneToOneField(ERPUser, on_delete=models.CASCADE, related_name='wallet')
    wallet_type= models.CharField(max_length=20, choices=WALLET_TYPE_CHOICES, default='general')
    balance= models.DecimalField(max_digits=16, decimal_places=2, default=0)
    last_dividend_check = models.DateField(blank=True, null=True)
    dividend_rate= models.DecimalField(max_digits=5, decimal_places=2, default=0)
    loan_balance= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Wallet - {self.user.full_name} ({self.wallet_type}) - {self.balance}'


class ERPWalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('commission', 'Commission'),
        ('incentive', 'Incentive'),
        ('bonus', 'Bonus'),
        ('dividend', 'Dividend'),
        ('withdrawal', 'Withdrawal'),
        ('loan_deduction', 'Loan Deduction'),
        ('survival_fund', 'Survival Fund'),
        ('ta_da', 'TA/DA'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    id = models.BigAutoField(primary_key=True)
    wallet = models.ForeignKey(ERPWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    booking = models.ForeignKey(
        ERPBooking, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='wallet_transactions'
    )
    receipt = models.ForeignKey(
        ERPMoneyReceipt, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='wallet_transactions'
    )
    description = models.TextField(blank=True, null=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.CharField(max_length=100, blank=True, null=True, default='')
    approved_at = models.DateTimeField(blank=True, null=True)
    is_holiday = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.wallet.user.full_name} - {self.transaction_type} - {self.amount}'


# =====================================================
# 14. COMMISSION****************(DONE)
# =====================================================

class ERPCommissionRule(models.Model):
    SOURCE_CHOICES = [
        ('booking', 'Booking Money'),
        ('installment', 'Installment'),
        ('down_payment', 'Down Payment'),
        ('investment', 'Investment'),
        ('registration', 'Registration'),
        ('land_dev', 'Land Development'),
        ('parking', 'Parking'),
        ('transfer', 'Transfer'),
        ('utility', 'Utility'),
    ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='commission_rules', null=True, blank=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES, null=True, blank=True)
    generation = models.IntegerField()
    percentage = models.DecimalField(max_digits=6, decimal_places=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['project', 'source_type', 'generation']
        ordering = ['generation']

    def __str__(self):
        return f"{self.project} - {self.source_type} - Gen {self.generation}"


class ERPCommission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('on_hold', 'On Hold'),
    ]

    marketing_officer = models.ForeignKey('ERPMarketingOfficer', on_delete=models.CASCADE, related_name='commissions')
    booking = models.ForeignKey('ERPBooking', on_delete=models.CASCADE, related_name='commissions')

    source_type = models.CharField(max_length=50, default='utility')
    generation = models.IntegerField()

    commission_rate = models.DecimalField(max_digits=6, decimal_places=3)
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    wallet_hit = models.BooleanField(default=True)
    wallet_hit_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.marketing_officer} - {self.commission_amount}"
    

# =====================================================
# 15. LOAN (DONE)
# =====================================================

class ERPLoan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ]

    id = models.BigAutoField(primary_key=True)

    # ✅ CASCADE → PROTECT — loan থাকলে user delete করতে দেবে না
    user = models.ForeignKey(
        ERPUser, on_delete=models.PROTECT,
        related_name='loans'
    )
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loan_date = models.DateField(default=date.today)
    reason = models.TextField(blank=True, null=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # ✅ CharField → FK
    approved_by = models.ForeignKey(
        'ERPUser', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_loans'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # ✅ নতুন loan এ remaining_amount auto set
        if not self.pk:
            self.remaining_amount = self.loan_amount

        # ✅ status auto-update
        if self.remaining_amount <= 0:
            self.status = 'paid'
        elif self.remaining_amount < self.loan_amount:
            self.status = 'partially_paid'
        else:
            self.status = 'active'

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Loan - {self.user.full_name} - {self.loan_amount}'


# =====================================================
# 16. INVESTOR***************(DONE)
# =====================================================


class ERPInvestor(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(ERPUser, on_delete=models.CASCADE, related_name='investor_profile')
    investor_code = models.CharField(max_length=50, unique=True, blank=True)
    marketing_officer = models.ForeignKey('ERPMarketingOfficer', on_delete=models.SET_NULL, null=True, blank=True, related_name='investors')
    bank_name = models.CharField(max_length=100, blank=True, null=True, default='')
    bank_account = models.CharField(max_length=50, blank=True, null=True, default='')
    bank_branch = models.CharField(max_length=100, blank=True, null=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(blank=True, null=True, default='')
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    nid_number = models.CharField(max_length=255, blank=True, null=True)
    nominee_details = models.TextField(max_length=255, blank=True, null=True)
    bank_account_details = models.TextField(blank=True, null=True, default='')

    def __str__(self):
        return f'{self.investor_code} - {self.user.full_name}'

    def save(self, *args, **kwargs):
        if not self.investor_code:
            with transaction.atomic():
                last = ERPInvestor.objects.select_for_update().order_by('-id').first()
                if last and last.investor_code:
                    try:
                        last_num = int(last.investor_code.split('-')[-1])
                    except ValueError:
                        last_num = 0
                else:
                    last_num = 0
                self.investor_code = f'ASH-{str(last_num + 1).zfill(4)}'
        super().save(*args, **kwargs)


class ERPInvestment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('matured', 'Matured'),
        ('cancelled', 'Cancelled'),
        ('withdrawn', 'Withdrawn'),
    ]

    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    investor = models.ForeignKey('ERPInvestor', on_delete=models.CASCADE, related_name='investments')
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='investments')
    investment_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    invest_amount = models.DecimalField(max_digits=16, decimal_places=2)
    invest_date = models.DateField(default=date.today)
    maturity_date = models.DateField(blank=True, null=True)
    monthly_dividend_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_profit_received = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    agreement_number = models.CharField(max_length=100, blank=True, null=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    cancellation_date = models.DateField(blank=True, null=True)
    cancellation_note = models.TextField(blank=True, null=True, default='')
    transferred_to_project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='transferred_investments')
    transfer_date = models.DateField(blank=True, null=True)
    transfer_service_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.CharField(max_length=50, default='12 Months')
    terms_conditions = models.TextField(blank=True, null=True)
    partial_return_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    amount_returned = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    dividend_payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    partial_return_date = models.DateField(blank=True, null=True)
    full_return_date = models.DateField(blank=True, null=True)
    documents = models.FileField(upload_to='investments/docs/', blank=True, null=True)
    audit_trail = models.JSONField(default=dict)

    @property
    def remaining_investment(self):
        return self.invest_amount - self.amount_returned

    def __str__(self):
        return f'{self.investor} - {self.invest_amount}'

    def save(self, *args, **kwargs):
        if not self.investment_id:
            with transaction.atomic():
                # id দিয়ে না, investment_id দিয়ে sort করো
                last = ERPInvestment.objects.select_for_update().filter(
                    investment_id__isnull=False
                ).order_by('-investment_id').first()
                
                if last and last.investment_id:
                    try:
                        last_num = int(last.investment_id.split('-')[-1])
                    except ValueError:
                        last_num = 0
                else:
                    last_num = 0
                self.investment_id = f'ID-{str(last_num + 1).zfill(4)}'
        super().save(*args, **kwargs)

        

class ERPDividend(models.Model):
    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('paid', 'Paid'),
        ('pending_withdrawal', 'Pending Withdrawal'),
    ]

    id = models.BigAutoField(primary_key=True)
    investment = models.ForeignKey(ERPInvestment, on_delete=models.CASCADE, related_name='dividends')
    investor = models.ForeignKey(ERPInvestor, on_delete=models.CASCADE, related_name='dividends')
    month = models.IntegerField()
    year = models.IntegerField()
    base_amount = models.DecimalField(max_digits=16, decimal_places=2)
    dividend_rate = models.DecimalField(max_digits=5, decimal_places=2)
    dividend_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='generated')
    wallet_credited = models.BooleanField(default=True)
    wallet_credited_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['investment', 'month', 'year']]
        ordering = ['-year', '-month']

    def __str__(self):
        return f'Dividend - {self.investor.investor_code} - {self.month}/{self.year}'



class LandPowerAssignment(models.Model):
    TRANSFER_STATUS = [
        ('pending', 'Pending'),
        ('transferred', 'Transferred'),
        ('completed', 'Completed'),
    ]
    
    CANCELLATION_CHOICES = [
        ('cancel', 'Cancel'),
        ('retain', 'Retain'),
    ]

    investment = models.OneToOneField(ERPInvestment, on_delete=models.CASCADE, related_name='land_power')
    land_power_assigned = models.DecimalField(max_digits=5, decimal_places=2) # Percentage
    conversion_ratio = models.DecimalField(max_digits=10, decimal_places=2)
    total_land_assigned = models.DecimalField(max_digits=5, decimal_places=2) # Percentage
    transfer_status = models.CharField(max_length=20, choices=TRANSFER_STATUS, default='pending')
    # Cancellation / Return
    cancellation_status = models.CharField(max_length=10, choices=CANCELLATION_CHOICES, blank=True)
    return_date = models.DateField(blank=True, null=True)
    reason_for_cancellation = models.TextField(blank=True, null=True)
    power_return_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    adjusted_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Land Power for {self.investment.investment_id}"


# =====================================================
# 17. HR — EMPLOYEE, ATTENDANCE, PAYROLL (DONE)
# =====================================================

class ERPEmployee(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('probation', 'Probation'),
        ('intern', 'Intern'),
    ]

    id               = models.BigAutoField(primary_key=True)
    user             = models.OneToOneField(
                           ERPUser, on_delete=models.SET_NULL,
                           null=True, blank=True,
                           related_name='employee_profile'
                       )
    employee_code    = models.CharField(max_length=50, unique=True, blank=True)
    department       = models.CharField(max_length=100, blank=True, null=True, default='')
    designation      = models.CharField(max_length=100, blank=True, null=True, default='')
    employment_type  = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='permanent')
    joining_date     = models.DateField(blank=True, null=True)
    basic_salary     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bank_name        = models.CharField(max_length=100, blank=True, null=True, default='')
    bank_account     = models.CharField(max_length=50, blank=True, null=True, default='')
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    # ── ERPUser থেকে delegate করা properties ──────────
    @property
    def full_name(self):
        return self.user.full_name if self.user else ''

    @property
    def phone(self):
        return self.user.phone if self.user else ''

    @property
    def email(self):
        return self.user.email if self.user else ''

    @property
    def address(self):
        return self.user.address if self.user else ''

    @property
    def nid(self):
        return self.user.nid if self.user else ''

    @property
    def profile_image(self):
        return self.user.image if self.user else None

    # ── Auto-generate employee_code ────────────────────
    @staticmethod
    def _generate_unique_code():
        with transaction.atomic():
            last = ERPEmployee.objects.select_for_update().order_by('-id').last()
            if last and last.employee_code:
                try:
                    last_num = int(last.employee_code.split('-')[-1])
                    next_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = ERPEmployee.objects.count() + 1
            else:
                next_num = 1

            while True:
                code = f"EMP-{next_num:04d}"
                if not ERPEmployee.objects.filter(employee_code=code).exists():
                    return code
                next_num += 1

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = self._generate_unique_code()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee_code} - {self.full_name}'
    

from django.db import models
from django.utils import timezone


class ERPAttendance(models.Model):
    STATUS_CHOICES = [
        ('present',  'Present'),
        ('absent',   'Absent'),
        ('late',     'Late'),
        ('half_day', 'Half Day'),
        ('leave',    'Leave'),
        ('holiday',  'Holiday'),
    ]

    id              = models.BigAutoField(primary_key=True)
    employee        = models.ForeignKey(ERPEmployee, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField()
    check_in        = models.DateTimeField(blank=True, null=True)
    check_out       = models.DateTimeField(blank=True, null=True)
    total_hours     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    device_log_id   = models.CharField(max_length=100, blank=True, null=True, default='')
    remarks         = models.TextField(blank=True, null=True, default='')
    marked_by       = models.CharField(max_length=100, blank=True, null=True, default='')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['employee', 'attendance_date']]
        ordering        = ['-attendance_date']

    def __str__(self):
        return f'{self.employee.full_name} - {self.attendance_date}'


class ERPAttendanceSummary(models.Model):
    employee     = models.ForeignKey(ERPEmployee, on_delete=models.CASCADE, related_name='attendance_summaries')
    month        = models.DateField()
    total_days   = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    absent_days  = models.IntegerField(default=0)
    late_days    = models.IntegerField(default=0)
    half_days    = models.IntegerField(default=0)
    leave_days   = models.IntegerField(default=0)
    holiday_days = models.IntegerField(default=0)
    total_hours  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['employee', 'month']]
        ordering        = ['-month']

    def __str__(self):
        return f'{self.employee.employee_code} - {self.month.strftime("%B %Y")}'


class ERPHoliday(models.Model):
    name         = models.CharField(max_length=200)
    date         = models.DateField(unique=True)
    holiday_type = models.CharField(max_length=50, choices=[
        ('govt',   'Government Holiday'),
        ('office', 'Office Holiday'),
        ('other',  'Other'),
    ], default='govt')
    description  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.name} - {self.date}'
        

class ERPPayroll(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(ERPEmployee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.IntegerField()
    year = models.IntegerField()
    working_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    payable_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowances = models.JSONField(default=dict, blank=True)
    deductions = models.JSONField(default=dict, blank=True)
    loan_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_date = models.DateField(blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_mode = models.CharField(max_length=50, blank=True, null=True, default='')
    created_by = models.CharField(max_length=100, blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['employee', 'month', 'year']]

    def __str__(self):
        return f'{self.employee.full_name} - {self.month}/{self.year}'


# =====================================================
# 18. OFFICER REQUEST (TA/DA/Mobile etc.)
# =====================================================

class ERPOfficerRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('ta', 'Travel Allowance (TA)'),
        ('da', 'Daily Allowance (DA)'),
        ('mobile_recharge', 'Mobile Recharge'),
        ('client_project_visit', 'Client Project Visit'),
        ('commission_withdrawal', 'Commission Withdrawal'),
        ('survival_fund', 'Survival Fund'),
        ('stl', 'STL'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    id = models.BigAutoField(primary_key=True)
    officer = models.ForeignKey(ERPMarketingOfficer, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True, default='')
    request_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.CharField(max_length=100, blank=True, null=True, default='')
    approved_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.officer.officer_code} - {self.request_type} - {self.amount}'


# =====================================================
# 19. ACCOUNT HEAD (DONE)
# =====================================================

class ERPAccountHead(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
    ]

    id = models.BigAutoField(primary_key=True)
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.account_code} - {self.account_name}'


# =====================================================
# 20. OFFER & DISCOUNT PORTAL (DONE)
# =====================================================

class ERPOffer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('discount', 'Discount'),
        ('gift', 'Gift'),
        ('special', 'Special Offer'),
        ('eid', 'Eid Offer'),
        ('seasonal', 'Seasonal'),
    ]

    TARGET_CHOICES = [
        ('all', 'All'),
        ('customer', 'Customers Only'),
        ('marketing', 'Marketing Officers Only'),
        ('new_booking', 'New Bookings'),
    ]

    id = models.BigAutoField(primary_key=True)
    offer_title = models.CharField(max_length=200)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='discount')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='offers')
    description = models.TextField(blank=True, null=True, default='')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gift_description = models.CharField(max_length=300, blank=True, null=True, default='')
    valid_from = models.DateField()
    valid_to = models.DateField()
    # ৯০ দিনের বেশি না
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    is_active = models.BooleanField(default=True)
    sms_sent = models.BooleanField(default=True)
    sms_sent_at = models.DateTimeField(blank=True, null=True)
    # created_by = models.CharField(max_length=100, blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.offer_title} - {self.valid_from} to {self.valid_to}'


# =====================================================
# 21. SMS LOG
# =====================================================

class ERPSMSLog(models.Model):
    SMS_TYPE_CHOICES = [
        ('installment_reminder', 'Installment Reminder (48h)'),
        ('installment_due', 'Installment Due'),
        ('payment_received', 'Payment Received'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('token_expiry', 'Token Expiry Warning'),
        ('cheque_deposit', 'Cheque Deposit Reminder'),
        ('welcome', 'Welcome'),
        ('offer', 'Offer'),
        ('eid', 'Eid Greetings'),
        ('jumar', 'Jumar Greetings'),
        ('pohela_boishakh', 'Pohela Boishakh'),
        ('commission', 'Commission Notification'),
        ('admin_notification', 'Admin Notification'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    id = models.BigAutoField(primary_key=True)
    recipient_phone = models.CharField(max_length=20)
    recipient_name  = models.CharField(max_length=200, blank=True, null=True, default='')
    sms_type = models.CharField(max_length=30, choices=SMS_TYPE_CHOICES)
    message  = models.TextField()
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sms_logs'
    )
    booking = models.ForeignKey(
        ERPBooking, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sms_logs'
    )
    officer = models.ForeignKey(
        ERPMarketingOfficer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sms_logs'
    )
    sent_at       = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True, default='')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'SMS - {self.recipient_phone} - {self.sms_type}'

# =====================================================
# 22. DOCUMENT
# =====================================================

class ERPDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('booking_mou', 'Booking MOU'),
        ('deed_draft', 'Deed Draft'),
        ('agreement', 'Agreement'),
        ('registration', 'Registration Document'),
        ('power_of_attorney', 'Power of Attorney'),
        ('namjari', 'Namjari'),
        ('porcha', 'Porcha'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    booking = models.ForeignKey(
        ERPBooking, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents'
    )
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents'
    )
    customer = models.ForeignKey(
        ERPCustomer, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents'
    )
    file = models.FileField(upload_to='erp/documents/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True, default='')

    # ✅ default=False
    is_signed = models.BooleanField(default=False)
    e_sign    = models.BooleanField(default=False)

    # ✅ CharField → FK
    created_by = models.ForeignKey(
        'ERPUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.document_type} - {self.title}'
# =====================================================
# 23. COMPANY ASSET (Logistics) (DONE)
# =====================================================

class ERPCompanyAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('mobile', 'Mobile Phone'),
        ('sim', 'SIM Card'),
        ('vehicle', 'Vehicle'),
        ('laptop', 'Laptop'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    asset_name = models.CharField(max_length=200)
    asset_code = models.CharField(max_length=50, blank=True, null=True, default='')
    assigned_to = models.ForeignKey(ERPUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    assigned_date = models.DateField(blank=True, null=True)
    returned_date = models.DateField(blank=True, null=True)
    condition = models.CharField(max_length=100, blank=True, null=True, default='')
    notes = models.TextField(blank=True, null=True, default='')
    is_returned = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.asset_type} - {self.asset_name}'


# =====================================================
# 24. SYSTEM LOG
# =====================================================

class ERPSystemLog(models.Model):
    LOG_LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        ERPUser, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    action      = models.CharField(max_length=200)
    module      = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, default='')
    ip_address  = models.GenericIPAddressField(blank=True, null=True)
    log_level   = models.CharField(max_length=20, choices=LOG_LEVEL_CHOICES, default='info')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} - {self.module}'


#======================================================
# 25.             LAND MANAGEMENT (DO)
#======================================================

import os


class ERPSupplier(models.Model):
    id                = models.BigAutoField(primary_key=True)
    supplier_code     = models.CharField(max_length=50, unique=True)   # e.g. ASLY-0001
    full_name         = models.CharField(max_length=200)
    phone             = models.CharField(max_length=50, blank=True, null=True, default='')
    email             = models.EmailField(max_length=150, blank=True, null=True, default='')
    address           = models.TextField(blank=True, null=True, default='')
    contract_details  = models.TextField(blank=True, null=True, default='')
    is_active         = models.BooleanField(default=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.supplier_code} - {self.full_name}'


class ERPLandOwner(models.Model):
    id                       = models.BigAutoField(primary_key=True)
    full_name                = models.CharField(max_length=200)
    nid                      = models.CharField(max_length=50, blank=True, null=True, default='')
    address                  = models.TextField(blank=True, null=True, default='')
    power_of_attorney_name   = models.CharField(max_length=200, blank=True, null=True, default='')
    power_of_attorney_doc    = models.FileField(
        upload_to='erp/land/attorney/', blank=True, null=True
    )
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class ERPLandAcquisition(models.Model):
    LAND_STATUS_CHOICES = [
        ('power_of_attorney', 'Power of Attorney'),
        ('saf_kabala',        'Saf-Kabala'),
    ]

    id= models.BigAutoField(primary_key=True)
    acquisition_code= models.CharField(max_length=50, unique=True)  # e.g. ACL-Land-0001
    supplier= models.ForeignKey(ERPSupplier, on_delete=models.SET_NULL,null=True, blank=True, related_name='land_acquisitions')
    land_owner= models.ForeignKey(ERPLandOwner, on_delete=models.SET_NULL,null=True, blank=True, related_name='land_acquisitions')

    # Khatiyan info
    khatiyan_number= models.CharField(max_length=100, blank=True, null=True, default='')

    # Area & price
    total_area= models.DecimalField(max_digits=14, decimal_places=4, default=0)  # Decimal SA,CS,RS,BRS
    price_per_decimal  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_value= models.DecimalField(max_digits=16, decimal_places=2, default=0)
    area_purchased= models.DecimalField(max_digits=14, decimal_places=4, default=0)
    amount_paid= models.DecimalField(max_digits=16, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_paid= models.DecimalField(max_digits=16, decimal_places=2, default=0)
    # Status
    land_status= models.CharField(max_length=30, choices=LAND_STATUS_CHOICES,default='power_of_attorney')
    is_mutated= models.BooleanField(default=False)   # mutation done?
    is_surveyed= models.BooleanField(default=False)   # surveyed?
    # Documents
    related_documents = models.FileField(upload_to='erp/land/documents/', blank=True, null=True)
    created_by= models.CharField(max_length=100, blank=True, null=True, default='')
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.acquisition_code}'

    def save(self, *args, **kwargs):
        # Auto-calculate outstanding & total_paid
        self.outstanding_amount = self.total_value - self.amount_paid
        self.total_paid         = self.amount_paid
        super().save(*args, **kwargs)



