from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from mainapp.models import (
    ERPUser, Project, Property, ERPLandRecord, ERPCustomer, ERPLead,
    ERPBooking, ERPInstallmentPlan, ERPMoneyReceipt, ERPVoucher,
    ERPProjectVisit, ERPMarketingOfficer, ERPWallet, ERPWalletTransaction,
    ERPCommissionRule, ERPCommission, ERPLoan, ERPInvestor, ERPInvestment,
    ERPDividend, ERPEmployee, ERPAttendance, ERPPayroll, ERPOfficerRequest,
    ERPAccountHead, ERPOffer, ERPSMSLog, ERPDocument, ERPCompanyAsset, ERPSystemLog,
    LandPowerAssignment,Transaction,ERPAttendanceSummary, ERPHoliday
)


# ===== 1. USER =====

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

# =====================================================
# ১. ইউজার লিস্ট দেখার জন্য সিরিয়ালাইজার
# =====================================================
class ERPUserListSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPUser
        fields = '__all__'

    def get_role_display(self, obj):
        if obj.roles:
            # role_name_example -> Role Name Example
            return ", ".join([r.replace('_', ' ').title() for r in obj.roles])
        return "N/A"


# =====================================================
# ২. ইউজারের ডিটেইলস এবং প্রোফাইল দেখার জন্য
# =====================================================
class ERPUserSerializer(serializers.ModelSerializer):
    is_customer = serializers.ReadOnlyField()
    is_investor = serializers.ReadOnlyField()
    is_marketingOfficer = serializers.ReadOnlyField()
    is_employee = serializers.ReadOnlyField()
    department_display = serializers.CharField(source='get_department_display', read_only=True)

    class Meta:
        model = ERPUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }


# =====================================================
# ৩. নতুন ইউজার তৈরি করার জন্য (রেজিস্ট্রেশন)
# =====================================================
from accesscontrol.serializers import ERPPermissionSerializer, ERPRolePermissionSerializer

class ERPUserCreateSerializer(serializers.ModelSerializer):
    password     = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    is_active    = serializers.BooleanField(default=True, required=False)
    roles        = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    is_employee  = serializers.ReadOnlyField()
    is_customer  = serializers.ReadOnlyField()
    is_investor  = serializers.ReadOnlyField()
    is_marketing = serializers.ReadOnlyField()

    class Meta:
        model  = ERPUser
        fields = [
            'id',
            'username',
            'email',
            'password',
            'full_name',
            'phone',
            'phone_alt',
            'present_address',
            'permanent_address',
            'father_name',
            'mother_name',
            'spouse_name',
            'nid',
            'nid_image',
            'date_of_birth',
            'image',
            'roles',
            'department',
            'is_active',
            'is_staff',
            'is_employee',
            'is_customer',
            'is_investor',
            'is_marketing',
            'last_login',
            'created_at',
            'updated_at',
            'referred_by',
        ]
        read_only_fields = [
            'id',
            'last_login',
            'created_at',
            'updated_at',
            'is_employee',
            'is_customer',
            'is_investor',
            'is_marketing',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user     = ERPUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    


#==========================================================
#ERPUserProfileSerializer
#==========================================================


class ERPUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPUser
        fields = [
            'id', 'username', 'email', 'full_name', 'phone',
            'phone_alt', 'present_address', 'permanent_address',
            'father_name', 'mother_name', 'spouse_name',
            'nid', 'nid_image', 'date_of_birth', 'image',
            'roles', 'department', 'loyalty_points',
            'is_active', 'last_login', 'created_at',
        ]
        read_only_fields = [
            'id', 'username', 'email', 'roles',
            'department', 'is_active',
            'last_login', 'created_at',
        ]


# ===== 2. PROJECT =====

class ERPProjectSerializer(serializers.ModelSerializer):
    project_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_project_type_display(self, obj): return obj.get_project_type_display()
    def get_status_display(self, obj): return obj.get_status_display()


# ===== 3. PLOT =====

class ERPPlotSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.project_name')
    project_code = serializers.ReadOnlyField(source='project.project_code')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_status_display(self, obj): return obj.get_status_display()



class FeaturedPlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = '__all__'


# ===== 4. LAND RECORD =====

class ERPLandRecordSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.project_name')
    land_status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPLandRecord
        fields = '__all__'

    def get_land_status_display(self, obj): return obj.get_land_status_display()



# ===== 5. CUSTOMER =====

class ERPCustomerSerializer(serializers.ModelSerializer):
    user    = ERPUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
                queryset=ERPUser.objects.all(),
                source='user',
                write_only=True    # ← True করুন, GET এ user object আসবে
              )
    
    is_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model  = ERPCustomer
        fields = [
            'id',
            'customer_code',
            'customer_type',
            'source',
            'user',        # GET এ পুরো object
            'user_id',     # POST/PATCH এ id পাঠাবেন
            'is_active',
            'created_by',
            'created_at',
            'updated_at',
        ]

# class ERPCustomerSerializer(serializers.ModelSerializer):
#     referred_by = serializers.SerializerMethodField()
#     class Meta:
#         model = ERPCustomer
#         fields = '__all__'

#     def get_referred_by(self, obj):
#         if obj.referred_by and obj.referred_by.username:
#             return obj.referred_by.username
#         return None

# ===== 6. LEAD =====

class ERPLeadSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    project_name = serializers.ReadOnlyField(source='interested_in.project_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPLead
        fields = '__all__'

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.user.full_name if obj.assigned_to else None

    def get_status_display(self, obj): return obj.get_status_display()



#======================================================
# TRANACTIONS TABLE
#=====================================================

class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    customer_name = serializers.CharField(source='customer.user.full_name', read_only=True)
    project_name  = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model  = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'booking',
            'customer', 'customer_name',
            'project', 'project_name',
            'plot',
            'user',
            'referred_by',
            'amount',
            'transferred_to',
            'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        transaction_type = data.get('transaction_type')
        transferred_to   = data.get('transferred_to')

        # 'transfer' type এ transferred_to থাকতে হবে
        if transaction_type == 'transfer' and not transferred_to:
            raise serializers.ValidationError({
                "transferred_to": "ট্রানজেকশন টাইপ 'Transfer' হলে কাকে ট্রান্সফার করা হচ্ছে (transferred_to) তা জানাতে হবে।"
            })

        # নিজেকে নিজে transfer করা যাবে না
        if transferred_to and data.get('customer') == transferred_to:
            raise serializers.ValidationError({
                "transferred_to": "একই কাস্টমারকে নিজের অ্যাকাউন্টে ট্রান্সফার করা যাবে না।"
            })

        return data
#=================================================
# Commission serialiazer
#=============================================

from mainapp.models import Commission

class CommissionSerializer(serializers.ModelSerializer):
    user_name    = serializers.ReadOnlyField(source='user.full_name')
    project_name = serializers.ReadOnlyField(source='project.project_name')
    plot_number  = serializers.ReadOnlyField(source='plot.plot_number')

    class Meta:
        model  = Commission
        fields = [
            'id', 'user', 'user_name',
            'project', 'project_name',
            'plot', 'plot_number',
            'level', 'percent', 'commission',
            'commission_type', 'note',
            'created_at', 'paid_at',
        ]
        read_only_fields = ['id', 'created_at']


        
# ===== 7. BOOKING =====

class ERPBookingSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    total_paid  = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    total_due   = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)

    class Meta:
        model  = ERPBooking
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Customer — user থাকলে full_name, না থাকলে customer_code fallback
        if instance.customer:
            representation['customer'] = (
                instance.customer.user.full_name
                if instance.customer.user
                else instance.customer.customer_code
            )
        else:
            representation['customer'] = None

        # Plot
        representation['plot'] = (
            instance.plot.plot_number if instance.plot else None
        )

        # Project
        representation['project'] = (
            instance.project.project_name if instance.project else None
        )

        # Marketing Officer
        if instance.marketing_officer and instance.marketing_officer.user:
            representation['marketing_officer'] = instance.marketing_officer.user.full_name
        else:
            representation['marketing_officer'] = None

        # Transferred To — user থাকলে full_name, না থাকলে customer_code fallback
        if instance.transferred_to:
            representation['transferred_to'] = (
                instance.transferred_to.user.full_name
                if instance.transferred_to.user
                else instance.transferred_to.customer_code
            )
        else:
            representation['transferred_to'] = None

        return representation
    
    
# ===== 8. INSTALLMENT PLAN =====

class ERPInstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPInstallmentPlan
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['booking_code'] = instance.booking.booking_code
        representation['customer_name'] = instance.booking.customer.user.full_name
        return representation


# ===== 9. MONEY RECEIPT =====

class ERPMoneyReceiptSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.full_name')
    booking_code = serializers.ReadOnlyField(source='booking.booking_code')
    status_display = serializers.SerializerMethodField()
    payment_mode_display = serializers.SerializerMethodField()
    receipt_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPMoneyReceipt
        fields = '__all__'

    def get_status_display(self, obj): return obj.get_status_display()
    def get_payment_mode_display(self, obj): return obj.get_payment_mode_display()
    def get_receipt_type_display(self, obj): return obj.get_receipt_type_display()


# ===== 10. VOUCHER =====


class ERPVoucherSerializer(serializers.ModelSerializer):
    # ✅ null check সহ
    voucher_number = serializers.CharField(required=False, read_only=True)
    customer_name = serializers.SerializerMethodField()
    booking_code = serializers.SerializerMethodField()
    voucher_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    # ✅ FK এর display name
    debit_head_name = serializers.SerializerMethodField()
    credit_head_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ERPVoucher
        fields = '__all__'

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def get_booking_code(self, obj):
        return obj.booking.booking_code if obj.booking else None

    def get_voucher_type_display(self, obj):
        return obj.get_voucher_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_debit_head_name(self, obj):
        return obj.debit_head.account_name if obj.debit_head else None

    def get_credit_head_name(self, obj):
        return obj.credit_head.account_name if obj.credit_head else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.full_name if obj.approved_by else None

    # ✅ approved voucher edit করা যাবে না
    def validate(self, data):
        if self.instance and self.instance.status == 'approved':
            raise serializers.ValidationError(
                'Approved voucher cannot be edited.'
            )
        return data
    



# ===== 11. PROJECT VISIT =====


class ERPProjectVisitSerializer(serializers.ModelSerializer):
    project_name      = serializers.SerializerMethodField()
    officer_name      = serializers.SerializerMethodField()
    customer_name     = serializers.SerializerMethodField()
    confirmed_by_name = serializers.SerializerMethodField()
    status_display    = serializers.SerializerMethodField()

    class Meta:
        model  = ERPProjectVisit
        fields = '__all__'

    def get_project_name(self, obj):
        return obj.project.project_name if obj.project else None

    def get_officer_name(self, obj):
        return obj.marketing_officer.user.full_name if obj.marketing_officer else None

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def get_confirmed_by_name(self, obj):
        return obj.confirmed_by.full_name if obj.confirmed_by else None

    def get_status_display(self, obj):
        return obj.get_status_display()

    def validate(self, data):
        new_status = data.get('status', getattr(self.instance, 'status', None))
        outcome    = data.get('outcome', getattr(self.instance, 'outcome', ''))
        if new_status in ['completed', 'no_show'] and not outcome:
            raise serializers.ValidationError(
                'Outcome is required when status is completed or no_show.'
            )
        return data
    

# ===== 12. MARKETING OFFICER =====


class ERPMarketingOfficerSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    user_phone = serializers.ReadOnlyField(source='user.phone')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_image = serializers.ImageField(source='user.image', read_only=True)
    rank_display = serializers.SerializerMethodField()
   
    class Meta:
        model = ERPMarketingOfficer
        fields = '__all__'

    def get_rank_display(self, obj): 
        return obj.get_rank_display()
    




# ===== 13. WALLET =====

class ERPWalletSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    wallet_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPWallet
        fields = '__all__'

    def get_wallet_type_display(self, obj): return obj.get_wallet_type_display()


class ERPWalletTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    transaction_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPWalletTransaction
        fields = '__all__'

    def get_user_name(self, obj): return obj.wallet.user.full_name if obj.wallet else None
    def get_transaction_type_display(self, obj): return obj.get_transaction_type_display()
    def get_status_display(self, obj): return obj.get_status_display()



class ERPCommissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPCommissionRule
        fields = '__all__'


class ERPCommissionSerializer(serializers.ModelSerializer):
    officer_name = serializers.SerializerMethodField()

    class Meta:
        model = ERPCommission
        fields = '__all__'

    def get_officer_name(self, obj):
        return obj.marketing_officer.user.full_name if obj.marketing_officer else None
    

# ===== 15. LOAN =====


class ERPLoanSerializer(serializers.ModelSerializer):
    employee_name    = serializers.SerializerMethodField()  # ✅ user_name → employee_name
    approved_by_name = serializers.SerializerMethodField()
    status_display   = serializers.SerializerMethodField()

    class Meta:
        model  = ERPLoan
        fields = '__all__'

    def get_employee_name(self, obj):                       # ✅
        return obj.employee.full_name if obj.employee else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.full_name if obj.approved_by else None

    def get_status_display(self, obj):
        return obj.get_status_display()

    def validate(self, data):
        loan_amount      = data.get('loan_amount',      getattr(self.instance, 'loan_amount',      0))
        remaining_amount = data.get('remaining_amount', getattr(self.instance, 'remaining_amount', 0))
        if remaining_amount > loan_amount:
            raise serializers.ValidationError(
                'Remaining amount cannot exceed loan amount.'
            )
        return data
    

# ===== 16. INVESTOR =====

class ERPInvestorSerializer(serializers.ModelSerializer):
    user_name  = serializers.ReadOnlyField(source='user.full_name')
    user_phone = serializers.ReadOnlyField(source='user.phone')
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model  = ERPInvestor
        fields = '__all__'


class ERPInvestmentSerializer(serializers.ModelSerializer):
    investor_code  = serializers.ReadOnlyField(source='investor.investor_code')
    investor_name  = serializers.SerializerMethodField()
    project_name   = serializers.ReadOnlyField(source='project.project_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model  = ERPInvestment
        fields = '__all__'

    def get_investor_name(self, obj):
        return obj.investor.user.full_name if obj.investor else None

    def get_status_display(self, obj):
        return obj.get_status_display()


class ERPDividendSerializer(serializers.ModelSerializer):
    investor_code  = serializers.ReadOnlyField(source='investor.investor_code')
    investor_name  = serializers.SerializerMethodField()
    investment_id  = serializers.ReadOnlyField(source='investment.investment_id')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model  = ERPDividend
        fields = '__all__'

    def get_investor_name(self, obj):
        return obj.investor.user.full_name if obj.investor else None

    def get_status_display(self, obj):
        return obj.get_status_display()


class LandPowerAssignmentSerializer(serializers.ModelSerializer):
    investment_code = serializers.ReadOnlyField(source='investment.investment_id')

    class Meta:
        model  = LandPowerAssignment
        fields = '__all__'

        

# ===== 17. EMPLOYEE =====

class ERPEmployeeSerializer(serializers.ModelSerializer):
    # ── ERPUser সব data ──
    user          = ERPUserSerializer(read_only=True)

    # ── read fields ──
    full_name         = serializers.SerializerMethodField()
    phone             = serializers.SerializerMethodField()
    email             = serializers.SerializerMethodField()
    present_address   = serializers.SerializerMethodField()
    permanent_address = serializers.SerializerMethodField()
    nid               = serializers.SerializerMethodField()
    profile_image     = serializers.SerializerMethodField()
    is_active         = serializers.SerializerMethodField()

    # ── display ──
    employment_type_display = serializers.SerializerMethodField()

    # ── write only ──
    user_id = serializers.IntegerField(write_only=True, required=True)

    def get_full_name(self, obj):          return obj.user.full_name if obj.user else ''
    def get_phone(self, obj):              return obj.user.phone if obj.user else ''
    def get_email(self, obj):              return obj.user.email if obj.user else ''
    def get_present_address(self, obj):    return obj.user.present_address if obj.user else ''
    def get_permanent_address(self, obj):  return obj.user.permanent_address if obj.user else ''
    def get_nid(self, obj):                return obj.user.nid if obj.user else ''
    def get_is_active(self, obj):          return obj.user.is_active if obj.user else False
    def get_employment_type_display(self, obj): return obj.get_employment_type_display()

    def get_profile_image(self, obj):
        if obj.user and obj.user.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.user.image.url) if request else obj.user.image.url
        return None

    class Meta:
        model  = ERPEmployee
        fields = [
            'id', 'employee_code',
            'user_id',                              # write only
            'user',                                 # সব user data
            'full_name', 'phone', 'email',          # read (shortcut)
            'present_address', 'permanent_address', # ← fixed
            'nid',
            'profile_image', 'is_active',
            'department', 'designation',
            'employment_type', 'employment_type_display',
            'joining_date',
            'basic_salary', 'bank_name', 'bank_account',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employee_code', 'created_at', 'updated_at']

    def validate_user_id(self, value):
        from mainapp.models import ERPUser
        try:
            user = ERPUser.objects.get(pk=value)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError('এই user পাওয়া যায়নি।')
        if hasattr(user, 'employee_profile') and user.employee_profile:
            raise serializers.ValidationError('এই user এর ইতিমধ্যে employee profile আছে।')
        return value

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        from mainapp.models import ERPUser
        user = ERPUser.objects.get(pk=user_id)

        roles = list(user.roles or [])
        if 'employee' not in roles:
            roles.append('employee')
            user.roles = roles
            user.save(update_fields=['roles'])

        validated_data['user'] = user
        return ERPEmployee.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user_id', None)
        return super().update(instance, validated_data)



from rest_framework import serializers
from django.utils import timezone
from datetime import time


# অফিস শুরুর সময় — এখান থেকে late নির্ধারণ হবে
OFFICE_START_TIME = time(9, 0, 0)   # সকাল ৯টা

from decimal import Decimal


class ERPAttendanceSerializer(serializers.ModelSerializer):
    employee_name  = serializers.ReadOnlyField(source='employee.full_name')
    employee_code  = serializers.ReadOnlyField(source='employee.employee_code')
    status_display = serializers.SerializerMethodField()
    total_hours    = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_total_hours(self, obj):
        if obj.check_in and obj.check_out:
            return round((obj.check_out - obj.check_in).total_seconds() / 3600, 2)
        return float(obj.total_hours)

    def validate(self, data):
        check_in  = data.get('check_in')
        check_out = data.get('check_out')

        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError({
                    'check_out': 'Check-out অবশ্যই check-in এর পরে হতে হবে।'
                })
            # ── total_hours auto calculate ──
            delta = check_out - check_in
            data['total_hours'] = Decimal(str(round(delta.total_seconds() / 3600, 2)))

        return data

    class Meta:
        model  = ERPAttendance
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ERPAttendanceSummarySerializer(serializers.ModelSerializer):
    employee_name   = serializers.ReadOnlyField(source='employee.full_name')
    employee_code   = serializers.ReadOnlyField(source='employee.employee_code')
    month_display   = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()

    def get_month_display(self, obj):
        return obj.month.strftime('%B %Y')

    def get_attendance_rate(self, obj):
        if obj.total_days == 0:
            return 0
        return round((obj.present_days / obj.total_days) * 100, 1)

    class Meta:
        model  = ERPAttendanceSummary
        fields = [
            'id', 'employee_code', 'employee_name',
            'month', 'month_display',
            'total_days', 'present_days', 'absent_days',
            'late_days', 'half_days', 'leave_days', 'holiday_days',
            'total_hours', 'attendance_rate',
            'created_at', 'updated_at',
        ]


class ERPCheckInSerializer(serializers.Serializer):
    """Device বা App থেকে check-in এর জন্য"""
    employee_id   = serializers.IntegerField()
    device_log_id = serializers.CharField(required=False, allow_blank=True)
    remarks       = serializers.CharField(required=False, allow_blank=True)

    def validate_employee_id(self, value):
        if not ERPEmployee.objects.filter(pk=value, user__is_active=True).exists():
            raise serializers.ValidationError('Employee পাওয়া যায়নি বা inactive।')
        return value


class ERPCheckOutSerializer(serializers.Serializer):
    """Device বা App থেকে check-out এর জন্য"""
    employee_id   = serializers.IntegerField()
    device_log_id = serializers.CharField(required=False, allow_blank=True)
    remarks       = serializers.CharField(required=False, allow_blank=True)

    def validate_employee_id(self, value):
        today = timezone.localdate()
        if not ERPAttendance.objects.filter(employee_id=value, attendance_date=today).exists():
            raise serializers.ValidationError('আজকের check-in পাওয়া যায়নি।')
        return value


class ERPHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model  = ERPHoliday
        fields = '__all__'



class ERPPayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    payment_status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPPayroll
        fields = '__all__'

    def get_payment_status_display(self, obj): return obj.get_payment_status_display()





# ===== 18. OFFICER REQUEST =====

class ERPOfficerRequestSerializer(serializers.ModelSerializer):
    officer_name = serializers.SerializerMethodField()
    officer_code = serializers.ReadOnlyField(source='officer.officer_code')
    request_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPOfficerRequest
        fields = '__all__'

    def get_officer_name(self, obj): return obj.officer.user.full_name if obj.officer else None
    def get_request_type_display(self, obj): return obj.get_request_type_display()
    def get_status_display(self, obj): return obj.get_status_display()


# ===== 19. ACCOUNT HEAD =====

class ERPAccountHeadSerializer(serializers.ModelSerializer):
    parent_name = serializers.ReadOnlyField(source='parent.account_name')
    account_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPAccountHead
        fields = '__all__'

    def get_account_type_display(self, obj): return obj.get_account_type_display()


# ===== 20. OFFER =====

class ERPOfferSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.project_name')
    offer_type_display = serializers.SerializerMethodField()
    target_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPOffer
        fields = '__all__'

    def get_offer_type_display(self, obj): return obj.get_offer_type_display()
    def get_target_display(self, obj): return obj.get_target_display()


# ===== 21. SMS LOG =====


class ERPSMSLogSerializer(serializers.ModelSerializer):
    sms_type_display = serializers.SerializerMethodField()
    status_display   = serializers.SerializerMethodField()

    # ✅ extra display fields
    customer_name = serializers.SerializerMethodField()
    booking_code  = serializers.SerializerMethodField()
    officer_name  = serializers.SerializerMethodField()

    class Meta:
        model  = ERPSMSLog
        fields = '__all__'

    def get_sms_type_display(self, obj):
        return obj.get_sms_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def get_booking_code(self, obj):
        return obj.booking.booking_code if obj.booking else None

    def get_officer_name(self, obj):
        return obj.officer.user.full_name if obj.officer else None
    


# ===== 22. DOCUMENT =====

class ERPDocumentSerializer(serializers.ModelSerializer):
    # ✅ null check সহ
    customer_name         = serializers.SerializerMethodField()
    booking_code          = serializers.SerializerMethodField()
    project_name          = serializers.SerializerMethodField()
    created_by_name       = serializers.SerializerMethodField()
    document_type_display = serializers.SerializerMethodField()

    class Meta:
        model  = ERPDocument
        fields = '__all__'

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None

    def get_booking_code(self, obj):
        return obj.booking.booking_code if obj.booking else None

    def get_project_name(self, obj):
        return obj.project.project_name if obj.project else None

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def get_document_type_display(self, obj):
        return obj.get_document_type_display()

    # ✅ file type validation
    def validate_file(self, value):
        if value:
            allowed = ['.pdf', '.jpg', '.jpeg', '.png']
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in allowed:
                raise serializers.ValidationError(
                    'Only PDF and image files (.pdf, .jpg, .jpeg, .png) are allowed.'
                )
        return value


# ===== 23. COMPANY ASSET =====

class ERPCompanyAssetSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    asset_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPCompanyAsset
        fields = '__all__'

    def get_assigned_to_name(self, obj): return obj.assigned_to.full_name if obj.assigned_to else None
    def get_asset_type_display(self, obj): return obj.get_asset_type_display()


# ===== 24. SYSTEM LOG =====

class ERPSystemLogSerializer(serializers.ModelSerializer):
    user_name         = serializers.SerializerMethodField()
    log_level_display = serializers.SerializerMethodField()

    class Meta:
        model  = ERPSystemLog
        fields = '__all__'

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_log_level_display(self, obj):
        return obj.get_log_level_display()

#======================================================
# 25.             LAND MANAGEMENT
#======================================================


from mainapp.models import ERPSupplier, ERPLandOwner, ERPLandAcquisition


class ERPSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ERPSupplier
        fields = '__all__'


class ERPLandOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ERPLandOwner
        fields = '__all__'


class ERPLandAcquisitionSerializer(serializers.ModelSerializer):
    supplier_name    = serializers.ReadOnlyField(source='supplier.full_name')
    supplier_code    = serializers.ReadOnlyField(source='supplier.supplier_code')
    land_owner_name  = serializers.ReadOnlyField(source='land_owner.full_name')
    land_status_display = serializers.SerializerMethodField()

    class Meta:
        model  = ERPLandAcquisition
        fields = '__all__'

    def get_land_status_display(self, obj):
        return obj.get_land_status_display()
    

# =====================================================
# 27. PERMISSION SERIALIZERS
# =====================================================

from accesscontrol.models import ERPPermission, ERPRolePermission


class ERPPermissionSerializer(serializers.ModelSerializer):
    module_display = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()

    class Meta:
        model  = ERPPermission
        fields = [
            'id', 'codename', 'module', 'module_display',
            'action', 'action_display', 'description', 'created_at'
        ]

    def get_module_display(self, obj): return obj.get_module_display()
    def get_action_display(self, obj): return obj.get_action_display()


class ERPRolePermissionSerializer(serializers.ModelSerializer):
    permission_codename = serializers.ReadOnlyField(source='permission.codename')
    permission_module   = serializers.ReadOnlyField(source='permission.module')
    permission_action   = serializers.ReadOnlyField(source='permission.action')
    scope_display       = serializers.SerializerMethodField()
    role_display        = serializers.SerializerMethodField()

    class Meta:
        model  = ERPRolePermission
        fields = [
            'id', 'role', 'role_display', 'permission',
            'permission_codename', 'permission_module', 'permission_action',
            'scope', 'scope_display', 'is_active',
            'updated_by', 'created_at', 'updated_at',
        ]
        validators = []  # ← unique_together block সরানো হয়েছে

    def get_scope_display(self, obj): return obj.get_scope_display()
    def get_role_display(self, obj):  return obj.get_role_display()

    def create(self, validated_data):
        obj, created = ERPRolePermission.objects.update_or_create(
            role=validated_data['role'],
            permission=validated_data['permission'],
            defaults={
                'scope':      validated_data.get('scope', 'own'),
                'is_active':  validated_data.get('is_active', True),
                'updated_by': validated_data.get('updated_by', None),
            }
        )
        return obj