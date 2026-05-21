from django.urls import path,include

from accesscontrol.permission_api import (
    ERPPermissionListView,
    ERPRolePermissionListView,
    ERPRolePermissionUpdateView,
    ERPRolePermissionCreateView,
    ERPRolePermissionDeleteView,
    role_permission_summary,
)

from mainapp.views import (
    # 1. User & Auth
    ERPUserListView,
    ERPUserDetailView,
    ERPUserCreateView,
    erp_user_login,
    ERPUserByRoleView,

    # 2. Project
    ERPProjectListView,
    ERPProjectDetailView,
    ERPProjectCreateView,

    # 3. Plot / Flat
    ERPPlotListView,
    ERPPlotDetailView,
    ERPPlotCreateView,
    FeaturedPlotListAPIView,

    # 4. Land Record
    ERPLandRecordListView,
    ERPLandRecordDetailView,
    ERPLandRecordCreateView,

    # 5. Customer
    ERPCustomerListView,
    ERPCustomerDetailView,
    ERPCustomerCreateView,

    # 6. Lead
    ERPLeadListView,
    ERPLeadDetailView,
    ERPLeadCreateView,

    # 7. Booking
    ERPBookingListView,
    ERPBookingDetailView,
    ERPBookingCreateView,

    # 8. Installment Plan
    ERPInstallmentPlanListView,
    ERPInstallmentUpdateView,
    ERPGenerateInstallmentScheduleView,
    ERPBookingSpecificInstallmentListView,

    # 9. Money Receipt
    ERPMoneyReceiptListView,
    ERPMoneyReceiptDetailView,
    ERPMoneyReceiptCreateView,
    ERPMoneyReceiptDownloadView,

    # 10. Voucher
    ERPVoucherListView,
    ERPVoucherDetailView,
    ERPVoucherCreateView,
    ERPVoucherRejectView,
    ERPVoucherApproveView,

    # 11. Project Visit
    ERPProjectVisitListView,
    ERPProjectVisitDetailView,
    ERPProjectVisitCreateView,

    # 12. Marketing Officer
    ERPMarketingOfficerListView,
    ERPMarketingOfficerDetailView,
    ERPMarketingOfficerCreateView,
    ERPMarketingOfficerDownlineView,

    # 13. Wallet
    ERPWalletListView,
    ERPWalletDetailView,
    ERPWalletByUserView,
    ERPWalletTransactionListView,
    ERPWalletTransactionDetailView,
    ERPWalletTransactionCreateView,

    # 14. Commission
    # ERPCommissionRuleListView,
    # ERPCommissionRuleDetailView,
    # ERPCommissionRuleCreateView,
    # ERPCommissionListView,
    # ERPCommissionDetailView,
    # ERPCommissionCreateView,
    officer_commission_detail,
    commission_dashboard,


    # 15. Loan
    ERPLoanListView,
    ERPLoanDetailView,
    ERPLoanCreateView,
    ERPLoanRepaymentView,

    # 16. Investor
    ERPInvestorListView,
    ERPInvestorDetailView,
    ERPInvestorCreateView,
    ERPInvestmentListView,
    ERPInvestmentDetailView,
    ERPInvestmentCreateView,
    ERPDividendListView,
    ERPDividendDetailView,
    ERPDividendCreateView,
    LandPowerViewSet,

    # 17. HR
    ERPEmployeeListView,
    ERPEmployeeDetailView,
    ERPEmployeeCreateView,
    ERPAttendanceListView,
    ERPAttendanceDetailView,
    ERPAttendanceCreateView,
    ERPPayrollListView,
    ERPPayrollDetailView,
    ERPPayrollCreateView,

    # 18. Officer Request
    ERPOfficerRequestListView,
    ERPOfficerRequestDetailView,
    ERPOfficerRequestCreateView,

    # 19. Account Head
    ERPAccountHeadListView,
    ERPAccountHeadDetailView,
    ERPAccountHeadCreateView,

    # 20. Offer
    ERPOfferListView,
    ERPOfferDetailView,
    ERPOfferCreateView,

    # 21. SMS Log
    ERPSMSLogListView,
    ERPSMSLogDetailView,
    ERPSMSLogCreateView,

    # 22. Document
    ERPDocumentListView,
    ERPDocumentDetailView,
    ERPDocumentCreateView,

    # 23. Company Asset
    ERPCompanyAssetListView,
    ERPCompanyAssetDetailView,
    ERPCompanyAssetCreateView,

    # 24. System Log
    ERPSystemLogListView,
    ERPSystemLogCreateView,
    ERPSystemLogDetailView,
    

    # 25. Land Management

    ERPSupplierListView, ERPSupplierCreateView, ERPSupplierDetailView,
    ERPLandOwnerListView, ERPLandOwnerCreateView, ERPLandOwnerDetailView,
    ERPLandAcquisitionListView, ERPLandAcquisitionCreateView, ERPLandAcquisitionDetailView,

    # Dashboard
    erp_dashboard_summary,

    CommissionListView,
    CommissionDetailView,
    CommissionCreateView,
    CommissionUpdateView,
    CommissionDeleteView,
    TransactionViewSet,

)

# =====================================================
# REAL ESTATE ERP — URL PATTERNS
# =====================================================

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'land-power', LandPowerViewSet)
router.register(r'transactions', TransactionViewSet, basename='transaction')
urlpatterns = [
    path('', include(router.urls)),
    path('', include(router.urls)),

    # =====================================================
    # 1. USER & AUTH
    # =====================================================
    path('erp-users/', ERPUserListView.as_view(), name='erp-user-list'),
    path('erp-users/<int:pk>/', ERPUserDetailView.as_view(), name='erp-user-detail'),
    path('erp-users/new/', ERPUserCreateView.as_view(), name='erp-user-create'),
    path('erp-users/login/', erp_user_login, name='erp-user-login'),
    path('erp-users/role/<str:role>/', ERPUserByRoleView.as_view(), name='erp-user-by-role'),

    # =====================================================
    # 2. PROJECT
    # =====================================================
    path('erp-projects/', ERPProjectListView.as_view(), name='erp-project-list'),
    path('erp-projects/<int:pk>/', ERPProjectDetailView.as_view(), name='erp-project-detail'),
    path('erp-projects/new/', ERPProjectCreateView.as_view(), name='erp-project-create'),

    # =====================================================
    # 3. PLOT / FLAT
    # ?project=<id>&status=<status>
    # =====================================================
    path('erp-plots/', ERPPlotListView.as_view(), name='erp-plot-list'),
    path('erp-plots/<int:pk>/', ERPPlotDetailView.as_view(), name='erp-plot-detail'),
    path('erp-plots/new/', ERPPlotCreateView.as_view(), name='erp-plot-create'),
    path('featured-plots/',FeaturedPlotListAPIView.as_view(),name='featured-plots'),

    # =====================================================
    # 4. LAND RECORD
    # ?project=<id>
    # =====================================================
    path('erp-land-records/', ERPLandRecordListView.as_view(), name='erp-land-record-list'),
    path('erp-land-records/<int:pk>/', ERPLandRecordDetailView.as_view(), name='erp-land-record-detail'),
    path('erp-land-records/new/', ERPLandRecordCreateView.as_view(), name='erp-land-record-create'),

    # =====================================================
    # 5. CUSTOMER
    # =====================================================
    path('erp-customers/', ERPCustomerListView.as_view(), name='erp-customer-list'),
    path('erp-customers/<int:pk>/', ERPCustomerDetailView.as_view(), name='erp-customer-detail'),
    path('erp-customers/new/', ERPCustomerCreateView.as_view(), name='erp-customer-create'),

    # =====================================================
    # 6. LEAD MANAGEMENT
    # ?assigned_to=<officer_id>&status=<status>
    # =====================================================
    path('erp-leads/', ERPLeadListView.as_view(), name='erp-lead-list'),
    path('erp-leads/<int:pk>/', ERPLeadDetailView.as_view(), name='erp-lead-detail'),
    path('erp-leads/new/', ERPLeadCreateView.as_view(), name='erp-lead-create'),

    # =====================================================
    # 7. BOOKING
    # ?customer=<id>&project=<id>&status=<status>
    # =====================================================
    path('erp-bookings/', ERPBookingListView.as_view(), name='erp-booking-list'),
    path('erp-bookings/<int:pk>/', ERPBookingDetailView.as_view(), name='erp-booking-detail'),
    path('erp-bookings/new/', ERPBookingCreateView.as_view(), name='erp-booking-create'),

    # =====================================================
    # 8. INSTALLMENT PLAN
    # ?booking=<id>
    # =====================================================
   # কিস্তির তালিকা দেখার জন্য
    path('erp-installments/', ERPInstallmentPlanListView.as_view(), name='installment-list'),
    # অটো শিডিউল জেনারেট করার জন্য (বুকিং আইডিসহ)
    path('erp-installments/new/', ERPGenerateInstallmentScheduleView.as_view(), name='installment-generate'),
    # নির্দিষ্ট কিস্তিতে পেমেন্ট বা আপডেট করার জন্য
    path('erp-installments/<int:pk>/', ERPInstallmentUpdateView.as_view(), name='installment-update'),
    # নির্দিষ্ট বুকিং কোডের কিস্তি দেখার জন্য
    path('erp-installments/<str:booking_code>/', ERPBookingSpecificInstallmentListView.as_view(), name='booking-specific-installments'),


    # =====================================================
    # 9. MONEY RECEIPT
    # ?booking=<id>&customer=<id>&status=pending|complete|authorized
    # =====================================================
    path('erp-receipts/', ERPMoneyReceiptListView.as_view(), name='erp-receipt-list'),
    path('erp-receipts/<int:pk>/', ERPMoneyReceiptDetailView.as_view(), name='erp-receipt-detail'),
    path('erp-receipts/new/', ERPMoneyReceiptCreateView.as_view(), name='erp-receipt-create'),
    path('receipts/download-pdf/<int:pk>/', ERPMoneyReceiptDownloadView.as_view(), name='receipt-download-pdf'),

    # =====================================================
    # 10. VOUCHER
    # ?type=debit|credit|journal|contra
    # =====================================================
    path('erp-vouchers/', ERPVoucherListView.as_view(), name='erp-voucher-list'),
    path('erp-vouchers/new/', ERPVoucherCreateView.as_view(), name='erp-voucher-create'),
    path('erp-vouchers/<int:pk>/', ERPVoucherDetailView.as_view(), name='erp-voucher-detail'),
    path('erp-vouchers/approve/<int:pk>/', ERPVoucherApproveView.as_view(), name='erp-voucher-approve'),
    path('erp-vouchers/reject/<int:pk>/', ERPVoucherRejectView.as_view(), name='erp-voucher-reject'),

    # =====================================================
    # 11. PROJECT VISIT
    # ?project=<id>&officer=<id>
    # =====================================================
    path('erp-visits/', ERPProjectVisitListView.as_view(), name='erp-visit-list'),
    path('erp-visits/new/', ERPProjectVisitCreateView.as_view(), name='erp-visit-create'),
    path('erp-visits/<int:pk>/', ERPProjectVisitDetailView.as_view(), name='erp-visit-detail'),

    # =====================================================
    # 12. MARKETING OFFICER
    # =====================================================
    path('erp-officers/', ERPMarketingOfficerListView.as_view(), name='erp-officer-list'),
    path('erp-officers/<int:pk>/', ERPMarketingOfficerDetailView.as_view(), name='erp-officer-detail'),
    path('erp-officers/new/', ERPMarketingOfficerCreateView.as_view(), name='erp-officer-create'),
    path('erp-officers/<int:pk>/downline/', ERPMarketingOfficerDownlineView.as_view(), name='erp-officer-downline'),

    # =====================================================
    # 13. WALLET
    # =====================================================
    path('erp-wallets/', ERPWalletListView.as_view(), name='erp-wallet-list'),
    path('erp-wallets/<int:pk>/', ERPWalletDetailView.as_view(), name='erp-wallet-detail'),
    path('erp-wallets/user/<int:user_id>/', ERPWalletByUserView.as_view(), name='erp-wallet-by-user'),

    # Wallet Transactions — ?wallet=<id>
    path('erp-wallet-transactions/', ERPWalletTransactionListView.as_view(), name='erp-wallet-transaction-list'),
    path('erp-wallet-transactions/<int:pk>/', ERPWalletTransactionDetailView.as_view(), name='erp-wallet-transaction-detail'),
    path('erp-wallet-transactions/new/', ERPWalletTransactionCreateView.as_view(), name='erp-wallet-transaction-create'),

    # =====================================================
    # 14. COMMISSION
    # =====================================================
    # path('erp-commission-rules/', ERPCommissionRuleListView.as_view(), name='erp-commission-rule-list'),
    # path('erp-commission-rules/<int:pk>/', ERPCommissionRuleDetailView.as_view(), name='erp-commission-rule-detail'),
    # path('erp-commission-rules/new/', ERPCommissionRuleCreateView.as_view(), name='erp-commission-rule-create'),

    # path('erp-commissions/', ERPCommissionListView.as_view(), name='erp-commission-list'),
    # path('erp-commissions/<int:pk>/', ERPCommissionDetailView.as_view(), name='erp-commission-detail'),
    # path('erp-commissions/new/', ERPCommissionCreateView.as_view(), name='erp-commission-create'),


    # # Commission Rules
    # path('commission-rules/', CommissionRuleListCreateView.as_view()),
    # path('commission-rules/<int:pk>/', CommissionRuleDetailView.as_view()),
    # # Commissions
    # path('commissions/', CommissionListView.as_view()),
    # path('commissions/<int:pk>/', CommissionDetailView.as_view()),
    # # Trigger Commission
    # path('generate-commission/', GenerateCommissionView.as_view()),

    path('commissions/',CommissionListView.as_view(),name='commission-list'),

    path('commissions/<int:pk>/',CommissionDetailView.as_view(),name='commission-detail'),

    path('commissions/create/',CommissionCreateView.as_view(),name='commission-create'),

    path('commissions/update/<int:pk>/',CommissionUpdateView.as_view(),name='commission-update'),

    path('commissions/delete/<int:pk>/',CommissionDeleteView.as_view(),name='commission-delete'),

    #from claude 
    path('commission-dashboard/', commission_dashboard, name='commission-dashboard'),
    path('commission-dashboard/officer/<int:officer_id>/', officer_commission_detail, name='officer-commission-detail'),

    # =====================================================
    # 15. LOAN
    # ?user=<id>
    # =====================================================
    path('erp-loans/', ERPLoanListView.as_view(), name='erp-loan-list'),
    path('erp-loans/new/', ERPLoanCreateView.as_view(), name='erp-loan-create'),
    path('erp-loans/<int:pk>/', ERPLoanDetailView.as_view(), name='erp-loan-detail'),
    path('erp-loans/<int:pk>/repay/', ERPLoanRepaymentView.as_view(), name='erp-loan-repay'),

    # =====================================================
    # 16. INVESTOR
    # =====================================================
    path('erp-investors/', ERPInvestorListView.as_view(), name='erp-investor-list'),
    path('erp-investors/<int:pk>/', ERPInvestorDetailView.as_view(), name='erp-investor-detail'),
    path('erp-investors/new/', ERPInvestorCreateView.as_view(), name='erp-investor-create'),

    path('erp-investments/', ERPInvestmentListView.as_view(), name='erp-investment-list'),
    path('erp-investments/<int:pk>/', ERPInvestmentDetailView.as_view(), name='erp-investment-detail'),
    path('erp-investments/new/', ERPInvestmentCreateView.as_view(), name='erp-investment-create'),

    path('erp-dividends/', ERPDividendListView.as_view(), name='erp-dividend-list'),
    path('erp-dividends/<int:pk>/', ERPDividendDetailView.as_view(), name='erp-dividend-detail'),
    path('erp-dividends/new/', ERPDividendCreateView.as_view(), name='erp-dividend-create'),

    # =====================================================
    # 17. HR — EMPLOYEE, ATTENDANCE, PAYROLL (DONE)
    # =====================================================
    path('erp-employees/', ERPEmployeeListView.as_view(), name='erp-employee-list'),
    path('erp-employees/new/', ERPEmployeeCreateView.as_view(), name='erp-employee-create'),  # ✅ আগে
    path('erp-employees/<int:pk>/', ERPEmployeeDetailView.as_view(), name='erp-employee-detail'),

    path('erp-attendance/', ERPAttendanceListView.as_view(), name='erp-attendance-list'),
    path('erp-attendance/new/', ERPAttendanceCreateView.as_view(), name='erp-attendance-create'),  # ✅ আগে
    path('erp-attendance/<int:pk>/', ERPAttendanceDetailView.as_view(), name='erp-attendance-detail'),

    path('erp-payroll/', ERPPayrollListView.as_view(), name='erp-payroll-list'),
    path('erp-payroll/new/', ERPPayrollCreateView.as_view(), name='erp-payroll-create'),  # ✅ আগে
    path('erp-payroll/<int:pk>/', ERPPayrollDetailView.as_view(), name='erp-payroll-detail'),

    # =====================================================
    # 18. OFFICER REQUEST (TA/DA/Mobile/Commission withdrawal)
    # ?officer=<id>&type=<type>&status=<status>
    # =====================================================
    path('erp-officer-requests/', ERPOfficerRequestListView.as_view(), name='erp-officer-request-list'),
    path('erp-officer-requests/<int:pk>/', ERPOfficerRequestDetailView.as_view(), name='erp-officer-request-detail'),
    path('erp-officer-requests/new/', ERPOfficerRequestCreateView.as_view(), name='erp-officer-request-create'),

    # =====================================================
    # 19. ACCOUNT HEAD (Chart of Accounts)
    # =====================================================
    path('erp-account-heads/', ERPAccountHeadListView.as_view(), name='erp-account-head-list'),
    path('erp-account-heads/<int:pk>/', ERPAccountHeadDetailView.as_view(), name='erp-account-head-detail'),
    path('erp-account-heads/new/', ERPAccountHeadCreateView.as_view(), name='erp-account-head-create'),

    # =====================================================
    # 20. OFFER PORTAL
    # ?project=<id>&active=true
    # =====================================================
    path('erp-offers/', ERPOfferListView.as_view(), name='erp-offer-list'),
    path('erp-offers/<int:pk>/', ERPOfferDetailView.as_view(), name='erp-offer-detail'),
    path('erp-offers/new/', ERPOfferCreateView.as_view(), name='erp-offer-create'),

    # =====================================================
    # 21. SMS LOG
    # ?customer=<id>&type=<sms_type>
    # =====================================================
    path('erp-sms-logs/', ERPSMSLogListView.as_view(), name='erp-sms-log-list'),
    path('erp-sms-logs/new/', ERPSMSLogCreateView.as_view(), name='erp-sms-log-create'),
    path('erp-sms-logs/<int:pk>/', ERPSMSLogDetailView.as_view(), name='erp-sms-log-detail'),

    # =====================================================
    # 22. DOCUMENT
    # ?booking=<id>&type=<doc_type>
    # =====================================================
    path('erp-documents/', ERPDocumentListView.as_view(), name='erp-document-list'),
    path('erp-documents/new/', ERPDocumentCreateView.as_view(), name='erp-document-create'),
    path('erp-documents/<int:pk>/', ERPDocumentDetailView.as_view(), name='erp-document-detail'),

    # =====================================================
    # 23. COMPANY ASSETS (Logistics)
    # ?assigned_to=<user_id>
    # =====================================================
    path('erp-assets/', ERPCompanyAssetListView.as_view(), name='erp-asset-list'),
    path('erp-assets/<int:pk>/', ERPCompanyAssetDetailView.as_view(), name='erp-asset-detail'),
    path('erp-assets/new/', ERPCompanyAssetCreateView.as_view(), name='erp-asset-create'),

    # =====================================================
    # 24. SYSTEM LOG
    # =====================================================
    path('erp-system-logs/', ERPSystemLogListView.as_view(), name='erp-system-log-list'),
    path('erp-system-logs/new/', ERPSystemLogCreateView.as_view(), name='erp-system-log-create'),
    path('erp-system-logs/<int:pk>/', ERPSystemLogDetailView.as_view(), name='erp-system-log-detail'),

    #======================================================
    # 25.             LAND MANAGEMENT
    #======================================================
    
    # Supplier
    path('erp-suppliers/',          ERPSupplierListView.as_view(),   name='erp-supplier-list'),
    path('erp-suppliers/new/',      ERPSupplierCreateView.as_view(), name='erp-supplier-create'),
    path('erp-suppliers/<int:pk>/', ERPSupplierDetailView.as_view(), name='erp-supplier-detail'),

    # Land Owner
    path('erp-land-owners/',          ERPLandOwnerListView.as_view(),   name='erp-land-owner-list'),
    path('erp-land-owners/new/',      ERPLandOwnerCreateView.as_view(), name='erp-land-owner-create'),
    path('erp-land-owners/<int:pk>/', ERPLandOwnerDetailView.as_view(), name='erp-land-owner-detail'),

    # Land Acquisition
    path('erp-land/',          ERPLandAcquisitionListView.as_view(),   name='erp-land-list'),
    path('erp-land/new/',      ERPLandAcquisitionCreateView.as_view(), name='erp-land-create'),
    path('erp-land/<int:pk>/', ERPLandAcquisitionDetailView.as_view(), name='erp-land-detail'),


    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================
    path('erp-dashboard/', erp_dashboard_summary, name='erp-dashboard'),
]

urlpatterns += [
    path('permissions/',                      ERPPermissionListView.as_view(),       name='permission-list'),
    path('role-permissions/',                 ERPRolePermissionListView.as_view(),   name='role-permission-list'),
    path('role-permissions/create/',          ERPRolePermissionCreateView.as_view(), name='role-permission-create'),
    path('role-permissions/<int:pk>/',        ERPRolePermissionUpdateView.as_view(), name='role-permission-update'),
    path('role-permissions/<int:pk>/delete/', ERPRolePermissionDeleteView.as_view(), name='role-permission-delete'),
    path('role-permission-summary/',          role_permission_summary,               name='role-permission-summary'),
]