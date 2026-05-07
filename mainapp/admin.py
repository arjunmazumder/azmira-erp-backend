from django.contrib import admin
from mainapp.models import (
    ERPUser,
    ERPProject,
    ERPPlot,
    ERPLandRecord,
    ERPCustomer,
    ERPLead,
    ERPBooking,
    ERPInstallmentPlan,
    ERPMoneyReceipt,
    ERPVoucher,
    ERPProjectVisit,
    ERPMarketingOfficer,
    ERPWallet,
    ERPWalletTransaction,
    ERPCommissionRule,
    ERPCommission,
    ERPLoan,
    ERPInvestor,
    ERPInvestment,
    ERPDividend,
    ERPEmployee,
    ERPAttendance,
    ERPPayroll,
    ERPOfficerRequest,
    ERPAccountHead,
    ERPOffer,
    ERPSMSLog,
    ERPDocument,
    ERPCompanyAsset,
    ERPSystemLog,
)


# =====================================================
# 1. USER
# =====================================================

@admin.register(ERPUser)
class ERPUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'full_name', 'email', 'roles', 'department', 'is_active', 'created_at')
    list_filter = ('roles', 'department', 'is_active', 'is_customer', 'is_investor', 'is_marketing')
    search_fields = ('username', 'full_name', 'email', 'phone', 'nid', 'employee_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    fieldsets = (
        ('Login Info', {
            'fields': ('username', 'email', 'password_hash')
        }),
        ('Personal Info', {
            'fields': ('full_name', 'phone', 'address', 'nid', 'date_of_birth', 'image')
        }),
        ('Role & Department', {
            'fields': ('roles', 'department', 'employee_id')
        }),
        ('Flags', {
            'fields': ('is_customer', 'is_investor', 'is_marketing', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 2. PROJECT
# =====================================================

@admin.register(ERPProject)
class ERPProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_code', 'project_name', 'project_type', 'status', 'total_plots', 'available_plots', 'created_at')
    list_filter = ('project_type', 'status', 'district')
    search_fields = ('project_code', 'project_name', 'city', 'district', 'mouza')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('project_code', 'project_name', 'project_type', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city', 'district', 'upazila', 'mouza')
        }),
        ('Land Info', {
            'fields': ('total_land_area', 'land_unit', 'total_plots', 'available_plots')
        }),
        ('Financial', {
            'fields': ('total_project_value',)
        }),
        ('Status & Dates', {
            'fields': ('status', 'launch_date', 'completion_date')
        }),
        ('Images', {
            'fields': ('image', 'layout_image')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 3. PLOT / FLAT
# =====================================================

@admin.register(ERPPlot)
class ERPPlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'plot_number', 'plot_type', 'area', 'area_unit', 'final_price', 'status')
    list_filter = ('project', 'plot_type', 'status', 'facing')
    search_fields = ('plot_number', 'flat_number', 'project__project_name', 'project__project_code')
    ordering = ('project', 'plot_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Plot Info', {
            'fields': ('project', 'plot_number', 'plot_type', 'status')
        }),
        ('Size', {
            'fields': ('area', 'area_unit', 'width', 'length', 'facing')
        }),
        ('Pricing', {
            'fields': ('price_per_unit', 'total_price', 'discount_amount', 'final_price')
        }),
        ('Flat Info (if applicable)', {
            'fields': ('floor_number', 'flat_number', 'bedrooms', 'bathrooms'),
            'classes': ('collapse',)
        }),
        ('Layout Position', {
            'fields': ('layout_x', 'layout_y'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 4. LAND RECORD
# =====================================================

@admin.register(ERPLandRecord)
class ERPLandRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'dag_number', 'khotian_number', 'mouza', 'total_area', 'land_status', 'namjari_done')
    list_filter = ('project', 'land_status', 'namjari_done')
    search_fields = ('dag_number', 'khotian_number', 'mouza', 'deed_number', 'land_owner_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Project', {
            'fields': ('project',)
        }),
        ('Land Identification', {
            'fields': ('dag_number', 'khotian_number', 'mouza')
        }),
        ('Area', {
            'fields': ('total_area', 'area_unit', 'purchased_area')
        }),
        ('Ownership & Deed', {
            'fields': ('land_owner_name', 'deed_number', 'deed_date', 'purchase_price')
        }),
        ('Status & Registration', {
            'fields': ('land_status', 'registration_date', 'registration_number', 'namjari_done', 'namjari_date', 'sub_registry_office')
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 5. CUSTOMER
# =====================================================

@admin.register(ERPCustomer)
class ERPCustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_code', 'full_name', 'phone', 'customer_type', 'source', 'referred_by', 'loyalty_points', 'is_active', 'created_at')
    list_filter = ('customer_type', 'source', 'is_active')
    search_fields = ('customer_code', 'full_name', 'phone', 'email', 'nid', 'father_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'customer_code', 'full_name', 'customer_type', 'source')
        }),
        ('Family Info', {
            'fields': ('father_name', 'mother_name', 'spouse_name')
        }),
        ('Contact', {
            'fields': ('phone', 'phone_alt', 'email', 'nid', 'date_of_birth')
        }),
        ('Address', {
            'fields': ('present_address', 'permanent_address')
        }),
        ('Marketing', {
            'fields': ('referred_by', 'loyalty_points')
        }),
        ('Images', {
            'fields': ('profile_image', 'nid_image')
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 6. LEAD
# =====================================================

@admin.register(ERPLead)
class ERPLeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_code', 'full_name', 'phone', 'source', 'status', 'assigned_to', 'next_follow_up', 'created_at')
    list_filter = ('status', 'source', 'assigned_to')
    search_fields = ('lead_code', 'full_name', 'phone', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'converted_at')
    fieldsets = (
        ('Lead Info', {
            'fields': ('lead_code', 'full_name', 'phone', 'email', 'address', 'source', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'interested_in')
        }),
        ('Follow Up', {
            'fields': ('next_follow_up', 'last_contacted', 'conversation_log')
        }),
        ('Conversion', {
            'fields': ('converted_customer', 'converted_at'),
            'classes': ('collapse',)
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 7. BOOKING
# =====================================================

class ERPInstallmentPlanInline(admin.TabularInline):
    model = ERPInstallmentPlan
    extra = 0
    fields = ('installment_number', 'due_date', 'amount', 'paid_amount', 'due_amount', 'is_paid',)
    readonly_fields = ('due_amount',)


class ERPMoneyReceiptInline(admin.TabularInline):
    model = ERPMoneyReceipt
    extra = 0
    fields = ('receipt_number', 'receipt_type', 'amount', 'payment_date', 'payment_mode', 'status')
    readonly_fields = ('receipt_number',)


@admin.register(ERPBooking)
class ERPBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_code', 'customer', 'project', 'plot', 'status', 'total_paid', 'total_due', 'token_expiry_date', 'booking_date')
    list_filter = ('status', 'project', 'token_status')
    search_fields = ('booking_code', 'customer__full_name', 'customer__phone', 'plot__plot_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_due')
    inlines = [ERPInstallmentPlanInline, ERPMoneyReceiptInline]
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_code', 'customer', 'plot', 'project', 'marketing_officer', 'booking_date', 'status')
        }),
        ('Pricing', {
            'fields': ('total_price', 'discount_amount', 'discount_note')
        }),
        ('Token / Booking Money', {
            'fields': ('token_amount', 'token_paid_date', 'token_expiry_date', 'token_status')
        }),
        ('Down Payment & Summary', {
            'fields': ('down_payment_amount', 'down_payment_date', 'total_paid', 'total_due')
        }),
        ('Cancellation / Refund', {
            'fields': ('cancel_reason', 'cancel_date', 'cancel_note', 'refund_amount', 'refund_date', 'refund_note'),
            'classes': ('collapse',)
        }),
        ('Transfer', {
            'fields': ('transferred_to', 'transfer_date', 'transfer_service_charge'),
            'classes': ('collapse',)
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 8. INSTALLMENT PLAN
# =====================================================

@admin.register(ERPInstallmentPlan)
class ERPInstallmentPlanAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'booking', 'installment_number',
        'due_date', 'amount', 'paid_amount',
        'due_amount', 'is_paid',
        'sms_sent_48h', 'sms_sent_due'
    )


# =====================================================
# 9. MONEY RECEIPT
# =====================================================

@admin.register(ERPMoneyReceipt)
class ERPMoneyReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'receipt_number', 'customer', 'booking', 'receipt_type', 'amount', 'payment_mode', 'status', 'payment_date')
    list_filter = ('status', 'payment_mode', 'receipt_type', 'e_sign', 'created_by_customer')
    search_fields = ('receipt_number', 'customer__full_name', 'booking__booking_code', 'cheque_number', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'e_sign_date', 'completed_at', 'authorized_at')
    fieldsets = (
        ('Receipt Info', {
            'fields': ('receipt_number', 'booking', 'customer', 'installment', 'receipt_type')
        }),
        ('Payment', {
            'fields': ('amount', 'payment_date', 'payment_mode', 'entry_date')
        }),
        ('Bank / Cheque', {
            'fields': ('bank_name', 'cheque_number', 'cheque_date', 'transaction_id', 'cheque_deposit_date', 'cheque_cleared', 'cheque_cleared_date', 'cheque_notification_sent'),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('status', 'e_sign', 'e_sign_date', 'created_by_customer', 'completed_by', 'completed_at', 'authorized_by', 'authorized_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 10. VOUCHER
# =====================================================

@admin.register(ERPVoucher)
class ERPVoucherAdmin(admin.ModelAdmin):
    list_display = ('id', 'voucher_number', 'voucher_type', 'amount', 'voucher_date', 'status', 'e_sign')
    list_filter = ('voucher_type', 'status', 'e_sign')
    search_fields = ('voucher_number', 'customer__full_name', 'booking__booking_code', 'debit_head', 'credit_head')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    fieldsets = (
        ('Voucher Info', {
            'fields': ('voucher_number', 'voucher_type', 'voucher_date', 'entry_date', 'amount', 'description')
        }),
        ('Links', {
            'fields': ('booking', 'customer')
        }),
        ('Accounts', {
            'fields': ('debit_head', 'credit_head')
        }),
        ('Approval', {
            'fields': ('status', 'e_sign', 'approved_by', 'approved_at')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 11. PROJECT VISIT
# =====================================================

@admin.register(ERPProjectVisit)
class ERPProjectVisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'guest_name', 'guest_phone', 'marketing_officer', 'visit_date', 'status', 'interested')
    list_filter = ('status', 'project', 'interested')
    search_fields = ('guest_name', 'guest_phone', 'project__project_name', 'marketing_officer__user__full_name')
    ordering = ('-visit_date',)
    readonly_fields = ('created_at', 'updated_at', 'confirmed_at')
    fieldsets = (
        ('Visit Info', {
            'fields': ('project', 'customer', 'lead', 'guest_name', 'guest_phone', 'visit_date', 'marketing_officer')
        }),
        ('Status', {
            'fields': ('status', 'interested', 'outcome')
        }),
        ('Confirmation', {
            'fields': ('confirmed_by', 'confirmed_at')
        }),
        ('Notifications', {
            'fields': ('notification_sent_24h', 'notification_sent_2h'),
            'classes': ('collapse',)
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 12. MARKETING OFFICER
# =====================================================

@admin.register(ERPMarketingOfficer)
class ERPMarketingOfficerAdmin(admin.ModelAdmin):
    list_display = ('id', 'officer_code', 'user', 'rank', 'upline', 'joining_date', 'commission_rate_lot', 'commission_rate_flat', 'is_active')
    list_filter = ('rank', 'is_active')
    search_fields = ('officer_code', 'user__full_name', 'user__phone', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'rank_achieved_at')
    fieldsets = (
        ('Officer Info', {
            'fields': ('user', 'officer_code', 'rank', 'rank_achieved_at', 'joining_date', 'is_active')
        }),
        ('Hierarchy', {
            'fields': ('upline',)
        }),
        ('Commission', {
            'fields': ('commission_rate_lot', 'commission_rate_flat', 'target_sales')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 13. WALLET
# =====================================================

@admin.register(ERPWallet)
class ERPWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet_type', 'balance', 'loan_balance', 'last_dividend_check')
    list_filter = ('wallet_type',)
    search_fields = ('user__full_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ERPWalletTransaction)
class ERPWalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'transaction_type', 'amount', 'balance_before', 'balance_after', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'is_holiday')
    search_fields = ('wallet__user__full_name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'approved_at')
    fieldsets = (
        ('Transaction', {
            'fields': ('wallet', 'transaction_type', 'amount', 'balance_before', 'balance_after', 'description')
        }),
        ('Links', {
            'fields': ('booking', 'receipt')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'is_holiday')
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 14. COMMISSION
# =====================================================

# @admin.register(ERPCommissionRule)
# class ERPCommissionRuleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'rule_name', 'project', 'generation', 'percentage', 'is_active', 'effective_from', 'effective_to')
#     list_filter = ('is_active', 'project', 'generation')
#     search_fields = ('rule_name',)
#     ordering = ('generation',)
#     readonly_fields = ('created_at',)


# @admin.register(ERPCommission)
# class ERPCommissionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'marketing_officer', 'booking', 'generation', 'commission_rate', 'commission_amount', 'is_cash_payment', 'status', 'wallet_hit')
#     list_filter = ('status', 'generation', 'is_cash_payment', 'wallet_hit')
#     search_fields = ('marketing_officer__officer_code', 'marketing_officer__user__full_name', 'booking__booking_code')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at', 'updated_at', 'wallet_hit_at')
#     fieldsets = (
#         ('Commission Info', {
#             'fields': ('marketing_officer', 'booking', 'receipt', 'generation')
#         }),
#         ('Amount', {
#             'fields': ('commission_rate', 'base_amount', 'commission_amount', 'payment_mode', 'is_cash_payment')
#         }),
#         ('Status', {
#             'fields': ('status', 'wallet_hit', 'wallet_hit_at')
#         }),
#         ('Audit', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )

from django.contrib import admin
from .models import ERPCommission, ERPCommissionRule

@admin.register(ERPCommissionRule)
class ERPCommissionRuleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project',
        'source_type',
        'generation',
        'percentage',
        'is_active'
    )

    list_filter = (
        'project',
        'source_type',
        'is_active'
    )

    search_fields = (
        'project__project_name',
    )


@admin.register(ERPCommission)
class ERPCommissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'marketing_officer',
        'booking',
        'source_type',
        'generation',
        'commission_amount',
        'status',
        'wallet_hit',
        'created_at'
    )

    list_filter = (
        'status',
        'source_type',
        'wallet_hit'
    )

    search_fields = (
        'marketing_officer__user__full_name',
        'booking__booking_code'
    )

    readonly_fields = (
        'created_at',
    )
# =====================================================
# 15. LOAN
# =====================================================

@admin.register(ERPLoan)
class ERPLoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'loan_amount', 'remaining_amount', 'loan_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__full_name', 'user__username', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    fieldsets = (
        ('Loan Info', {
            'fields': ('user', 'loan_amount', 'remaining_amount', 'loan_date', 'reason', 'status')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 16. INVESTOR
# =====================================================

@admin.register(ERPInvestor)
class ERPInvestorAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor_code', 'user', 'bank_name', 'bank_account', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('investor_code', 'user__full_name', 'user__phone', 'bank_account')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ERPInvestment)
class ERPInvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'project', 'invest_amount', 'invest_date', 'maturity_date', 'monthly_dividend_rate', 'total_profit_received', 'status')
    list_filter = ('status', 'project')
    search_fields = ('investor__investor_code', 'investor__user__full_name', 'agreement_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Investment Info', {
            'fields': ('investor', 'project', 'invest_amount', 'invest_date', 'maturity_date', 'agreement_number', 'status')
        }),
        ('Dividend', {
            'fields': ('monthly_dividend_rate', 'total_profit_received')
        }),
        ('Cancellation', {
            'fields': ('cancellation_date', 'cancellation_note'),
            'classes': ('collapse',)
        }),
        ('Asset Transfer', {
            'fields': ('transferred_to_project', 'transfer_date', 'transfer_service_charge'),
            'classes': ('collapse',)
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ERPDividend)
class ERPDividendAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'investment', 'month', 'year', 'base_amount', 'dividend_rate', 'dividend_amount', 'status', 'wallet_credited')
    list_filter = ('status', 'wallet_credited', 'year', 'month')
    search_fields = ('investor__investor_code', 'investor__user__full_name')
    ordering = ('-year', '-month')
    readonly_fields = ('created_at', 'wallet_credited_at')


# =====================================================
# 17. HR
# =====================================================

@admin.register(ERPEmployee)
class ERPEmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee_code', 'full_name', 'department', 'designation', 'employment_type', 'basic_salary', 'is_active', 'joining_date')
    list_filter = ('employment_type', 'is_active', 'department')
    search_fields = ('employee_code', 'full_name', 'phone', 'email', 'nid')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Employee Info', {
            'fields': ('user', 'employee_code', 'full_name', 'department', 'designation', 'employment_type', 'joining_date', 'is_active')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'address', 'nid')
        }),
        ('Salary & Bank', {
            'fields': ('basic_salary', 'bank_name', 'bank_account')
        }),
        ('Image', {
            'fields': ('profile_image',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ERPAttendance)
class ERPAttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'attendance_date', 'check_in', 'check_out', 'total_hours', 'status')
    list_filter = ('status', 'attendance_date')
    search_fields = ('employee__full_name', 'employee__employee_code', 'device_log_id')
    ordering = ('-attendance_date',)
    readonly_fields = ('created_at',)


@admin.register(ERPPayroll)
class ERPPayrollAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'month', 'year', 'basic_salary', 'payable_salary', 'loan_deduction', 'net_salary', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'year', 'month')
    search_fields = ('employee__full_name', 'employee__employee_code')
    ordering = ('-year', '-month')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Payroll Info', {
            'fields': ('employee', 'month', 'year', 'working_days', 'present_days')
        }),
        ('Salary', {
            'fields': ('basic_salary', 'payable_salary', 'allowances', 'deductions', 'loan_deduction', 'net_salary')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_date', 'payment_mode')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 18. OFFICER REQUEST (TA/DA/Mobile/Commission etc.)
# =====================================================

@admin.register(ERPOfficerRequest)
class ERPOfficerRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'officer', 'request_type', 'amount', 'request_date', 'status', 'approved_by')
    list_filter = ('request_type', 'status')
    search_fields = ('officer__officer_code', 'officer__user__full_name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    fieldsets = (
        ('Request Info', {
            'fields': ('officer', 'request_type', 'amount', 'description', 'request_date')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 19. ACCOUNT HEAD
# =====================================================

@admin.register(ERPAccountHead)
class ERPAccountHeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_code', 'account_name', 'account_type', 'parent', 'opening_balance', 'current_balance', 'is_active')
    list_filter = ('account_type', 'is_active')
    search_fields = ('account_code', 'account_name')
    ordering = ('account_code',)
    readonly_fields = ('created_at',)


# =====================================================
# 20. OFFER PORTAL
# =====================================================

@admin.register(ERPOffer)
class ERPOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer_title', 'offer_type', 'project', 'target', 'valid_from', 'valid_to', 'is_active', 'sms_sent')
    list_filter = ('offer_type', 'target', 'is_active', 'sms_sent')
    search_fields = ('offer_title', 'description', 'gift_description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'sms_sent_at')
    fieldsets = (
        ('Offer Info', {
            'fields': ('offer_title', 'offer_type', 'project', 'description', 'target')
        }),
        ('Discount / Gift', {
            'fields': ('discount_amount', 'discount_percentage', 'gift_description')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('SMS', {
            'fields': ('sms_sent', 'sms_sent_at')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 21. SMS LOG
# =====================================================

@admin.register(ERPSMSLog)
class ERPSMSLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_phone', 'recipient_name', 'sms_type', 'status', 'sent_at', 'created_at')
    list_filter = ('sms_type', 'status')
    search_fields = ('recipient_phone', 'recipient_name', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'sent_at')
    fieldsets = (
        ('Recipient', {
            'fields': ('recipient_phone', 'recipient_name', 'customer', 'booking', 'officer')
        }),
        ('Message', {
            'fields': ('sms_type', 'message', 'status', 'error_message')
        }),
        ('Timing', {
            'fields': ('sent_at', 'created_at'),
        }),
    )


# =====================================================
# 22. DOCUMENT
# =====================================================

@admin.register(ERPDocument)
class ERPDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_type', 'title', 'booking', 'customer', 'project', 'is_signed', 'e_sign', 'created_at')
    list_filter = ('document_type', 'is_signed', 'e_sign')
    search_fields = ('title', 'booking__booking_code', 'customer__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Document Info', {
            'fields': ('document_type', 'title', 'booking', 'project', 'customer')
        }),
        ('File & Notes', {
            'fields': ('file', 'notes')
        }),
        ('Signing', {
            'fields': ('is_signed', 'e_sign')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 23. COMPANY ASSET (LOGISTICS)
# =====================================================

@admin.register(ERPCompanyAsset)
class ERPCompanyAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_type', 'asset_name', 'asset_code', 'assigned_to', 'assigned_date', 'returned_date', 'is_returned')
    list_filter = ('asset_type', 'is_returned')
    search_fields = ('asset_name', 'asset_code', 'assigned_to__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Asset Info', {
            'fields': ('asset_type', 'asset_name', 'asset_code', 'condition')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_date', 'returned_date', 'is_returned')
        }),
        ('Notes & Audit', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================
# 24. SYSTEM LOG
# =====================================================

@admin.register(ERPSystemLog)
class ERPSystemLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'module', 'log_level', 'ip_address', 'created_at')
    list_filter = ('log_level', 'module')
    search_fields = ('action', 'module', 'description', 'user__full_name', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)