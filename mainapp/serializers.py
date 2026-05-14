from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from mainapp.models import (
    ERPUser, ERPProject, ERPPlot, ERPLandRecord, ERPCustomer, ERPLead,
    ERPBooking, ERPInstallmentPlan, ERPMoneyReceipt, ERPVoucher,
    ERPProjectVisit, ERPMarketingOfficer, ERPWallet, ERPWalletTransaction,
    ERPCommissionRule, ERPCommission, ERPLoan, ERPInvestor, ERPInvestment,
    ERPDividend, ERPEmployee, ERPAttendance, ERPPayroll, ERPOfficerRequest,
    ERPAccountHead, ERPOffer, ERPSMSLog, ERPDocument, ERPCompanyAsset, ERPSystemLog,
    LandPowerAssignment
)


# ===== 1. USER =====


# class ERPUserSerializer(serializers.ModelSerializer):
#     # roles এখন লিস্ট, তাই আমরা ম্যানুয়ালি এটি ডিসপ্লে করার জন্য মেথড লিখব
#     role_display = serializers.SerializerMethodField()
#     department_display = serializers.SerializerMethodField()

#     class Meta:
#         model = ERPUser
#         fields = '__all__'
#         extra_kwargs = {'password_hash': {'write_only': True}}

#     def get_role_display(self, obj):
#         # JSONField/List এর জন্য কাস্টম ডিসপ্লে লজিক
#         if obj.roles:
#             # আন্ডারস্কোর বাদ দিয়ে এবং টাইটেল কেস করে দেখাবে (যেমন: admin -> Admin)
#             return ", ".join([r.replace('_', ' ').title() for r in obj.roles])
#         return "No Role"

#     def get_department_display(self, obj):
#         # Department এখনো ChoiceField তাই এটি কাজ করবে
#         return obj.get_department_display() if obj.department else None


class ERPUserListSerializer(serializers.ModelSerializer):
    # লিস্ট ভিউতে 'role' এর বদলে 'roles' ব্যবহার করতে হবে
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPUser
        fields = ['id', 'username', 'full_name', 'email', 'roles', 'role_display', 'department', 'is_active']

    def get_role_display(self, obj):
        if obj.roles:
            return ", ".join([r.replace('_', ' ').title() for r in obj.roles])
        return "N/A"


class ERPUserSerializer(serializers.ModelSerializer):
    is_customer = serializers.SerializerMethodField()
    is_investor = serializers.SerializerMethodField()
    is_marketing = serializers.SerializerMethodField()
    department_display = serializers.SerializerMethodField()
    class Meta:
        model = ERPUser
        fields = '__all__'
        extra_kwargs = {'password_hash': {'write_only': True}}

    def get_is_customer(self, obj): return obj.is_customer
    def get_is_investor(self, obj): return obj.is_investor
    def get_is_marketing(self, obj): return obj.is_marketing
    def get_department_display(self, obj):
        return obj.get_department_display() if obj.department else None

class ERPUserCreateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )

    class Meta:
        model = ERPUser
        fields = [
            'id', 'username', 'email', 'password', 'full_name', 'phone',
            'address', 'nid', 'date_of_birth', 'image', 'roles',
            'department', 'employee_id', 'is_active',
            # is_customer, is_investor, is_marketing বাদ — এগুলো property
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = ERPUser.objects.create(**validated_data)
        if password:
            user.password_hash = make_password(password)
            user.save(update_fields=['password_hash'])
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



class FeaturedPlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = ERPPlot
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
    referred_by = serializers.SerializerMethodField()
    class Meta:
        model = ERPCustomer
        fields = '__all__'

    def get_referred_by(self, obj):
        if obj.referred_by and obj.referred_by.username:
            return obj.referred_by.username
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
    # ক্যালকুলেটেড ফিল্ডগুলো read_only রাখা ভালো যাতে ইউজার ইনপুট না দিতে পারে
    final_price = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    total_due = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)

    class Meta:
        model = ERPBooking
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # রিলেশনাল ফিল্ডগুলোর নাম দেখানো
        representation['customer'] = instance.customer.full_name if instance.customer else None
        representation['plot'] = instance.plot.plot_number if instance.plot else None
        representation['project'] = instance.project.project_name if instance.project else None
        
        # Marketing Officer হ্যান্ডেল করা
        if instance.marketing_officer and instance.marketing_officer.user:
            representation['marketing_officer'] = instance.marketing_officer.user.full_name
        else:
            representation['marketing_officer'] = None

        # Transfer Information
        representation['transferred_to'] = instance.transferred_to.full_name if instance.transferred_to else None
            
        return representation

# ===== 8. INSTALLMENT PLAN =====

class ERPInstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPInstallmentPlan
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # রিলেশন থেকে তথ্য দেখানো
        representation['booking_code'] = instance.booking.booking_code
        representation['customer_name'] = instance.booking.customer.full_name
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
    project_name = serializers.SerializerMethodField()
    officer_name = serializers.SerializerMethodField()

    # ✅ null check সহ
    customer_name = serializers.SerializerMethodField()
    confirmed_by_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPProjectVisit
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
        # ✅ completed/no_show হলে outcome দিতে হবে
        new_status = data.get('status', getattr(self.instance, 'status', None))
        outcome = data.get('outcome', getattr(self.instance, 'outcome', ''))
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

# class ERPCommissionRuleSerializer(serializers.ModelSerializer):
#     project_name = serializers.ReadOnlyField(source='project.project_name')

#     class Meta:
#         model = ERPCommissionRule
#         fields = '__all__'


# class ERPCommissionSerializer(serializers.ModelSerializer):
#     officer_name = serializers.SerializerMethodField()
#     booking_code = serializers.ReadOnlyField(source='booking.booking_code')
#     status_display = serializers.SerializerMethodField()

#     class Meta:
#         model = ERPCommission
#         fields = '__all__'

#     def get_officer_name(self, obj):
#         return obj.marketing_officer.user.full_name if obj.marketing_officer else None

#     def get_status_display(self, obj): return obj.get_status_display()



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
    # ✅ null check সহ
    user_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ERPLoan
        fields = '__all__'

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.full_name if obj.approved_by else None

    def get_status_display(self, obj):
        return obj.get_status_display()

    def validate(self, data):
        # ✅ remaining_amount loan_amount এর চেয়ে বেশি হতে পারবে না
        loan_amount = data.get('loan_amount', getattr(self.instance, 'loan_amount', 0))
        remaining = data.get('remaining_amount', getattr(self.instance, 'remaining_amount', 0))
        if remaining > loan_amount:
            raise serializers.ValidationError(
                'Remaining amount cannot exceed loan amount.'
            )
        return data


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

class LandPowerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandPowerAssignment
        fields = '__all__'


# ===== 17. HR PayRoll =====

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