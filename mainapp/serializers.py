from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from mainapp.models import (
    ERPUser, ERPProject, ERPPlot, ERPLandRecord, ERPCustomer, ERPLead,
    ERPBooking, ERPInstallmentPlan, ERPMoneyReceipt, ERPVoucher,
    ERPProjectVisit, ERPMarketingOfficer, ERPWallet, ERPWalletTransaction,
    ERPCommissionRule, ERPCommission, ERPLoan, ERPInvestor, ERPInvestment,
    ERPDividend, ERPEmployee, ERPAttendance, ERPPayroll, ERPOfficerRequest,
    ERPAccountHead, ERPOffer, ERPSMSLog, ERPDocument, ERPCompanyAsset, ERPSystemLog,
)


# ===== 1. USER =====

class ERPUserSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    department_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPUser
        fields = '__all__'
        extra_kwargs = {'password_hash': {'write_only': True}}

    def get_role_display(self, obj): return obj.get_role_display()
    def get_department_display(self, obj): return obj.get_department_display() if obj.department else None


class ERPUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPUser
        fields = ['id', 'username', 'full_name', 'email', 'role', 'department', 'is_active']

class ERPUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    # এখানে ডিফল্ট ভ্যালু সেট করে দিন
    is_active = serializers.BooleanField(default=True) 

    class Meta:
        model = ERPUser
        fields = ['id', 'username', 'email', 'password', 'full_name', 'phone', 'address',
                  'nid', 'date_of_birth', 'image', 'role', 'department', 'employee_id',
                  'is_customer', 'is_investor', 'is_marketing', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # এখানে validated_data-তে is_active না থাকলেও ডিফল্ট True পাবে
        user = ERPUser.objects.create(**validated_data) 
        if password:
            user.password_hash = make_password(password)
            user.save()
        return user
# ===== 2. PROJECT =====

class ERPProjectSerializer(serializers.ModelSerializer):
    project_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPProject
        fields = '__all__'

    def get_project_type_display(self, obj): return obj.get_project_type_display()
    def get_status_display(self, obj): return obj.get_status_display()


# ===== 3. PLOT =====

class ERPPlotSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.project_name')
    project_code = serializers.ReadOnlyField(source='project.project_code')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPPlot
        fields = '__all__'

    def get_status_display(self, obj): return obj.get_status_display()


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
    referred_by = serializers.SerializerMethodField()
    class Meta:
        model = ERPCustomer
        fields = '__all__'

    def get_referred_by(self, obj):
        if obj.referred_by and obj.referred_by.user:
            return obj.referred_by.user.full_name
        return None

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


# ===== 7. BOOKING =====

class ERPBookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.full_name')
    customer_code = serializers.ReadOnlyField(source='customer.customer_code')
    plot_number = serializers.ReadOnlyField(source='plot.plot_number')
    project_name = serializers.ReadOnlyField(source='project.project_name')
    officer_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPBooking
        fields = '__all__'

    def get_officer_name(self, obj):
        return obj.marketing_officer.user.full_name if obj.marketing_officer else None

    def get_status_display(self, obj): return obj.get_status_display()


# ===== 8. INSTALLMENT PLAN =====

class ERPInstallmentPlanSerializer(serializers.ModelSerializer):
    booking_code = serializers.ReadOnlyField(source='booking.booking_code')
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = ERPInstallmentPlan
        fields = '__all__'

    def get_customer_name(self, obj):
        return obj.booking.customer.full_name if obj.booking else None


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
    customer_name = serializers.ReadOnlyField(source='customer.full_name')
    booking_code = serializers.ReadOnlyField(source='booking.booking_code')
    voucher_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPVoucher
        fields = '__all__'

    def get_voucher_type_display(self, obj): return obj.get_voucher_type_display()
    def get_status_display(self, obj): return obj.get_status_display()


# ===== 11. PROJECT VISIT =====

class ERPProjectVisitSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.project_name')
    officer_name = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source='customer.full_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPProjectVisit
        fields = '__all__'

    def get_officer_name(self, obj):
        return obj.marketing_officer.user.full_name if obj.marketing_officer else None

    def get_status_display(self, obj): return obj.get_status_display()


# ===== 12. MARKETING OFFICER =====

class ERPMarketingOfficerSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    user_phone = serializers.ReadOnlyField(source='user.phone')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_image = serializers.ImageField(source='user.image', read_only=True)
    rank_display = serializers.SerializerMethodField()
    upline_name = serializers.SerializerMethodField()

    class Meta:
        model = ERPMarketingOfficer
        fields = '__all__'

    def get_rank_display(self, obj): return obj.get_rank_display()
    def get_upline_name(self, obj): return obj.upline.user.full_name if obj.upline else None


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


# ===== 14. COMMISSION =====

class ERPCommissionRuleSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.project_name')

    class Meta:
        model = ERPCommissionRule
        fields = '__all__'


class ERPCommissionSerializer(serializers.ModelSerializer):
    officer_name = serializers.SerializerMethodField()
    booking_code = serializers.ReadOnlyField(source='booking.booking_code')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPCommission
        fields = '__all__'

    def get_officer_name(self, obj):
        return obj.marketing_officer.user.full_name if obj.marketing_officer else None

    def get_status_display(self, obj): return obj.get_status_display()


# ===== 15. LOAN =====

class ERPLoanSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPLoan
        fields = '__all__'

    def get_status_display(self, obj): return obj.get_status_display()


# ===== 16. INVESTOR =====

class ERPInvestorSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    user_phone = serializers.ReadOnlyField(source='user.phone')
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = ERPInvestor
        fields = '__all__'


class ERPInvestmentSerializer(serializers.ModelSerializer):
    investor_code = serializers.ReadOnlyField(source='investor.investor_code')
    investor_name = serializers.SerializerMethodField()
    project_name = serializers.ReadOnlyField(source='project.project_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPInvestment
        fields = '__all__'

    def get_investor_name(self, obj): return obj.investor.user.full_name if obj.investor else None
    def get_status_display(self, obj): return obj.get_status_display()


class ERPDividendSerializer(serializers.ModelSerializer):
    investor_code = serializers.ReadOnlyField(source='investor.investor_code')
    investor_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPDividend
        fields = '__all__'

    def get_investor_name(self, obj): return obj.investor.user.full_name if obj.investor else None
    def get_status_display(self, obj): return obj.get_status_display()


# ===== 17. HR =====

class ERPEmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    employment_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPEmployee
        fields = '__all__'

    def get_user_name(self, obj): return obj.user.full_name if obj.user else None
    def get_employment_type_display(self, obj): return obj.get_employment_type_display()


class ERPAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPAttendance
        fields = '__all__'

    def get_status_display(self, obj): return obj.get_status_display()


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
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPSMSLog
        fields = '__all__'

    def get_sms_type_display(self, obj): return obj.get_sms_type_display()
    def get_status_display(self, obj): return obj.get_status_display()


# ===== 22. DOCUMENT =====

class ERPDocumentSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.full_name')
    booking_code = serializers.ReadOnlyField(source='booking.booking_code')
    project_name = serializers.ReadOnlyField(source='project.project_name')
    document_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPDocument
        fields = '__all__'

    def get_document_type_display(self, obj): return obj.get_document_type_display()


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
    user_name = serializers.SerializerMethodField()
    log_level_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPSystemLog
        fields = '__all__'

    def get_user_name(self, obj): return obj.user.full_name if obj.user else None
    def get_log_level_display(self, obj): return obj.get_log_level_display()