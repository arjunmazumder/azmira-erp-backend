# api/views.py
# Real Estate ERP — Complete views based on models.py and serializers.py

from django.contrib.auth.hashers import make_password, check_password
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from datetime import datetime, date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from decimal import Decimal

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

from .serializers import (
    ERPUserSerializer,
    ERPUserCreateSerializer,
    ERPUserListSerializer,
    ERPProjectSerializer,
    ERPPlotSerializer,
    ERPLandRecordSerializer,
    ERPCustomerSerializer,
    ERPLeadSerializer,
    ERPBookingSerializer,
    ERPInstallmentPlanSerializer,
    ERPMoneyReceiptSerializer,
    ERPVoucherSerializer,
    ERPProjectVisitSerializer,
    ERPMarketingOfficerSerializer,
    ERPWalletSerializer,
    ERPWalletTransactionSerializer,
    ERPCommissionRuleSerializer,
    ERPCommissionSerializer,
    ERPLoanSerializer,
    ERPInvestorSerializer,
    ERPInvestmentSerializer,
    ERPDividendSerializer,
    ERPEmployeeSerializer,
    ERPAttendanceSerializer,
    ERPPayrollSerializer,
    ERPOfficerRequestSerializer,
    ERPAccountHeadSerializer,
    ERPOfferSerializer,
    ERPSMSLogSerializer,
    ERPDocumentSerializer,
    ERPCompanyAssetSerializer,
    ERPSystemLogSerializer,
)


# =====================================================
# 1. USER & AUTH VIEWS
# =====================================================

class ERPUserListView(generics.ListAPIView):
    """GET /api/erp-users/ — all user list"""
    queryset = ERPUser.objects.all()

    def get_serializer_class(self):
        if self.request.query_params.get('list'):
            return ERPUserListSerializer
        return ERPUserSerializer


class ERPUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/erp-users/<pk>/"""
    queryset = ERPUser.objects.all()
    serializer_class = ERPUserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_update(self, serializer):
        password = self.request.data.get('password')
        if password:
            serializer.save(password_hash=make_password(password))
        else:
            serializer.save()


class ERPUserCreateView(generics.CreateAPIView):
    queryset = ERPUser.objects.all()
    serializer_class = ERPUserCreateSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def erp_user_login(request):
    """POST /api/erp-users/login/"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'success': False, 'message': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = ERPUser.objects.get(username=username)

        if check_password(password, user.password_hash):
            if not user.is_active:
                return Response(
                    {'success': False, 'message': 'Account is deactivated'},
                    status=status.HTTP_403_FORBIDDEN
                )

            user.last_login = datetime.now()
            user.save(update_fields=['last_login'])

            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'message': 'Login successful',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': ERPUserSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response(
            {'success': False, 'message': 'Invalid password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    except ERPUser.DoesNotExist:
        return Response(
            {'success': False, 'message': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class ERPUserByRoleView(generics.ListAPIView):
    """GET /api/erp-users/role/<role>/"""
    serializer_class = ERPUserListSerializer

    def get_queryset(self):
        return ERPUser.objects.filter(roles__contains=[self.kwargs['role']], is_active=True)


# =====================================================
# 2. PROJECT VIEWS
# =====================================================

class ERPProjectListView(generics.ListAPIView):
    queryset = ERPProject.objects.all()
    serializer_class = ERPProjectSerializer


class ERPProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPProject.objects.all()
    serializer_class = ERPProjectSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPProjectCreateView(generics.CreateAPIView):
    queryset = ERPProject.objects.all()
    serializer_class = ERPProjectSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


# =====================================================
# 3. PLOT / FLAT VIEWS
# =====================================================

class ERPPlotListView(generics.ListAPIView):
    """GET /api/erp-plots/ — ?project=<id>&status=<status>"""
    serializer_class = ERPPlotSerializer

    def get_queryset(self):
        qs = ERPPlot.objects.all()
        project_id = self.request.query_params.get('project')
        status_filter = self.request.query_params.get('status')
        if project_id:
            qs = qs.filter(project_id=project_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class ERPPlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPPlot.objects.all()
    serializer_class = ERPPlotSerializer


class ERPPlotCreateView(generics.CreateAPIView):
    queryset = ERPPlot.objects.all()
    serializer_class = ERPPlotSerializer


# =====================================================
# 4. LAND RECORD VIEWS
# =====================================================

class ERPLandRecordListView(generics.ListAPIView):
    """GET /api/erp-land-records/ — ?project=<id>"""
    serializer_class = ERPLandRecordSerializer

    def get_queryset(self):
        qs = ERPLandRecord.objects.all()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class ERPLandRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPLandRecord.objects.all()
    serializer_class = ERPLandRecordSerializer


class ERPLandRecordCreateView(generics.CreateAPIView):
    queryset = ERPLandRecord.objects.all()
    serializer_class = ERPLandRecordSerializer


# =====================================================
# 5. CUSTOMER VIEWS
# =====================================================

class ERPCustomerListView(generics.ListAPIView):
    queryset = ERPCustomer.objects.all()
    serializer_class = ERPCustomerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPCustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPCustomer.objects.all()
    serializer_class = ERPCustomerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPCustomerCreateView(generics.CreateAPIView):
    queryset = ERPCustomer.objects.all()
    serializer_class = ERPCustomerSerializer

    def perform_create(self, serializer):
        serializer.save(is_active=True)


# =====================================================
# 6. LEAD VIEWS
# =====================================================

class ERPLeadListView(generics.ListAPIView):
    """GET /api/erp-leads/ — ?assigned_to=<officer_id>&status=<status>"""
    serializer_class = ERPLeadSerializer

    def get_queryset(self):
        qs = ERPLead.objects.all()
        assigned_to = self.request.query_params.get('assigned_to')
        lead_status = self.request.query_params.get('status')
        if assigned_to:
            qs = qs.filter(assigned_to_id=assigned_to)
        if lead_status:
            qs = qs.filter(status=lead_status)
        return qs


class ERPLeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPLead.objects.all()
    serializer_class = ERPLeadSerializer


class ERPLeadCreateView(generics.CreateAPIView):
    queryset = ERPLead.objects.all()
    serializer_class = ERPLeadSerializer


# =====================================================
# 7. BOOKING VIEWS
# =====================================================

class ERPBookingListView(generics.ListAPIView):
    """GET /api/erp-bookings/ — ?customer=<id>&project=<id>&status=<status>"""
    serializer_class = ERPBookingSerializer

    def get_queryset(self):
        qs = ERPBooking.objects.all()
        customer_id = self.request.query_params.get('customer')
        project_id = self.request.query_params.get('project')
        booking_status = self.request.query_params.get('status')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if project_id:
            qs = qs.filter(project_id=project_id)
        if booking_status:
            qs = qs.filter(status=booking_status)
        return qs


class ERPBookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPBooking.objects.all()
    serializer_class = ERPBookingSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        if 'down_payment_amount' in request.data:
            self._recalculate_installments(booking)
            booking.refresh_from_db()

        return Response(self.get_serializer(booking).data)

    def _recalculate_installments(self, booking):
        unpaid_installments = booking.installment_plan.filter(is_paid=False)
        count = unpaid_installments.count()

        if count > 0:
            per_installment = booking.total_due / count
            for inst in unpaid_installments:
                inst.amount = round(per_installment, 2)
                inst.due_amount = inst.amount - inst.paid_amount
                inst.save()


class ERPBookingCreateView(generics.CreateAPIView):
    queryset = ERPBooking.objects.all()
    serializer_class = ERPBookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        if booking.plot:
            booking.plot.status = 'booked'
            booking.plot.save()

        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)


# =====================================================
# 8. INSTALLMENT PLAN VIEWS
# =====================================================

from dateutil.relativedelta import relativedelta


class ERPInstallmentPlanListView(generics.ListAPIView):
    queryset = ERPInstallmentPlan.objects.all()
    serializer_class = ERPInstallmentPlanSerializer


class ERPBookingSpecificInstallmentListView(generics.ListAPIView):
    """
    নির্দিষ্ট একটি booking_code এর আন্ডারে সব কিস্তির লিস্ট দেখাবে।
    Example URL: /api/installments/BK-2024-001/
    """
    serializer_class = ERPInstallmentPlanSerializer

    def get_queryset(self):
        booking_code = self.kwargs['booking_code']
        return ERPInstallmentPlan.objects.filter(booking__booking_code=booking_code)


class ERPInstallmentUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ERPInstallmentPlan.objects.all()
    serializer_class = ERPInstallmentPlanSerializer


class ERPGenerateInstallmentScheduleView(APIView):
    """
    booking_code ব্যবহার করে পুরো কিস্তি শিডিউল জেনারেট করার লজিক।
    Input: booking_code, number_of_installments, start_date
    """
    def post(self, request):
        booking_code = request.data.get('booking_code')
        num_inst_raw = request.data.get('number_of_installments')
        start_date_str = request.data.get('start_date')

        if not all([booking_code, num_inst_raw, start_date_str]):
            return Response(
                {"error": "booking_code, number_of_installments and start_date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            num_inst = int(num_inst_raw)

            try:
                booking = ERPBooking.objects.get(booking_code=booking_code)
            except ERPBooking.DoesNotExist:
                return Response(
                    {"error": f"Booking with code {booking_code} not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            booking.installment_plan.all().delete()

            total_to_distribute = booking.total_due

            if total_to_distribute <= 0:
                return Response(
                    {"error": "Total due is 0. No installments needed."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            amount_per_inst = round(total_to_distribute / num_inst, 2)
            current_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

            installments = []
            cumulative_amount = Decimal('0.00')

            for i in range(1, num_inst + 1):
                if i == num_inst:
                    inst_amount = total_to_distribute - cumulative_amount
                else:
                    inst_amount = Decimal(str(amount_per_inst))
                    cumulative_amount += inst_amount

                installments.append(ERPInstallmentPlan(
                    booking=booking,
                    installment_number=i,
                    due_date=current_date,
                    amount=inst_amount,
                    due_amount=inst_amount
                ))
                current_date += relativedelta(months=1)

            ERPInstallmentPlan.objects.bulk_create(installments)

            return Response(
                {"message": f"Successfully generated {num_inst} installments for booking {booking_code}."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =====================================================
# 9. MONEY RECEIPT VIEWS
# =====================================================

from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse


class ERPMoneyReceiptListView(generics.ListAPIView):
    """GET /api/erp-receipts/ — ?booking=<id>&customer=<id>&status=<status>"""
    serializer_class = ERPMoneyReceiptSerializer

    def get_queryset(self):
        qs = ERPMoneyReceipt.objects.all()
        booking_id = self.request.query_params.get('booking')
        customer_id = self.request.query_params.get('customer')
        receipt_status = self.request.query_params.get('status')
        if booking_id:
            qs = qs.filter(booking_id=booking_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if receipt_status:
            qs = qs.filter(status=receipt_status)
        return qs


class ERPMoneyReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """3-stage approval: pending → complete → authorized. No backdated entry."""
    queryset = ERPMoneyReceipt.objects.all()
    serializer_class = ERPMoneyReceiptSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        new_status = request.data.get('status')

        if new_status == 'complete' and instance.status == 'pending':
            instance.completed_by = request.data.get('completed_by', '')
            instance.completed_at = datetime.now()
        elif new_status == 'authorized' and instance.status == 'complete':
            instance.authorized_by = request.data.get('authorized_by', '')
            instance.authorized_at = datetime.now()
            instance.e_sign = True
            instance.e_sign_date = datetime.now()
            self._update_booking_payment(instance)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(instance).data)

    def _update_booking_payment(self, receipt):
        """When receipt is authorized, update booking total_paid."""
        booking = receipt.booking
        booking.total_paid += receipt.amount
        booking.total_due = booking.final_price - booking.total_paid
        booking.save()
        if receipt.installment:
            inst = receipt.installment
            inst.paid_amount += receipt.amount
            inst.due_amount = inst.amount - inst.paid_amount
            if inst.paid_amount >= inst.amount:
                inst.is_paid = True
            inst.save()


class ERPMoneyReceiptCreateView(generics.CreateAPIView):
    queryset = ERPMoneyReceipt.objects.all()
    serializer_class = ERPMoneyReceiptSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receipt = serializer.save()
        return Response(self.get_serializer(receipt).data, status=status.HTTP_201_CREATED)


class ERPMoneyReceiptDownloadView(generics.RetrieveAPIView):
    queryset = ERPMoneyReceipt.objects.all()

    def get(self, request, *args, **kwargs):
        receipt_obj = self.get_object()
        amount_in_words = f"BDT: {receipt_obj.amount} Taka Only."

        context = {
            'receipt': receipt_obj,
            'amount_in_words': amount_in_words,
            'generated_at': datetime.now().strftime("%d-%m-%Y %H:%M %p"),
        }

        html_string = render_to_string('pdf/money_receipt.html', context)
        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Receipt_{receipt_obj.receipt_number}.pdf"'
        return response


# =====================================================
# 10. VOUCHER VIEWS
# =====================================================

class ERPVoucherListView(generics.ListAPIView):
    """GET /api/erp-vouchers/ — ?type=debit|credit|journal|contra"""
    serializer_class = ERPVoucherSerializer

    def get_queryset(self):
        qs = ERPVoucher.objects.all()
        v_type = self.request.query_params.get('type')
        if v_type:
            qs = qs.filter(voucher_type=v_type)
        return qs


class ERPVoucherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPVoucher.objects.all()
    serializer_class = ERPVoucherSerializer


class ERPVoucherCreateView(generics.CreateAPIView):
    queryset = ERPVoucher.objects.all()
    serializer_class = ERPVoucherSerializer


# =====================================================
# 11. PROJECT VISIT VIEWS
# =====================================================

class ERPProjectVisitListView(generics.ListAPIView):
    """GET /api/erp-visits/ — ?project=<id>&officer=<id>"""
    serializer_class = ERPProjectVisitSerializer

    def get_queryset(self):
        qs = ERPProjectVisit.objects.all()
        project_id = self.request.query_params.get('project')
        officer_id = self.request.query_params.get('officer')
        if project_id:
            qs = qs.filter(project_id=project_id)
        if officer_id:
            qs = qs.filter(marketing_officer_id=officer_id)
        return qs


class ERPProjectVisitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPProjectVisit.objects.all()
    serializer_class = ERPProjectVisitSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.data.get('status') == 'confirmed' and not instance.confirmed_by:
            instance.confirmed_by = request.data.get('confirmed_by', '')
            instance.confirmed_at = datetime.now()
            instance.save()
        serializer.save()
        return Response(self.get_serializer(instance).data)


class ERPProjectVisitCreateView(generics.CreateAPIView):
    queryset = ERPProjectVisit.objects.all()
    serializer_class = ERPProjectVisitSerializer


# =====================================================
# 12. MARKETING OFFICER VIEWS
# =====================================================

class ERPMarketingOfficerListView(generics.ListAPIView):
    queryset = ERPMarketingOfficer.objects.filter(is_active=True)
    serializer_class = ERPMarketingOfficerSerializer


class ERPMarketingOfficerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPMarketingOfficer.objects.all()
    serializer_class = ERPMarketingOfficerSerializer


class ERPMarketingOfficerCreateView(generics.CreateAPIView):
    queryset = ERPMarketingOfficer.objects.all()
    serializer_class = ERPMarketingOfficerSerializer


class ERPMarketingOfficerDownlineView(generics.ListAPIView):
    """GET /api/erp-officers/<pk>/downline/"""
    serializer_class = ERPMarketingOfficerSerializer

    def get_queryset(self):
        officer_id = self.kwargs['pk']
        return ERPMarketingOfficer.objects.filter(upline_id=officer_id, is_active=True)


# =====================================================
# 13. WALLET VIEWS
# =====================================================

class ERPWalletListView(generics.ListAPIView):
    queryset = ERPWallet.objects.all()
    serializer_class = ERPWalletSerializer


class ERPWalletDetailView(generics.RetrieveUpdateAPIView):
    queryset = ERPWallet.objects.all()
    serializer_class = ERPWalletSerializer


class ERPWalletByUserView(generics.ListAPIView):
    """GET /api/erp-wallets/user/<user_id>/"""
    serializer_class = ERPWalletSerializer

    def get_queryset(self):
        return ERPWallet.objects.filter(user_id=self.kwargs['user_id'])


class ERPWalletTransactionListView(generics.ListAPIView):
    """GET /api/erp-wallet-transactions/ — ?wallet=<id>"""
    serializer_class = ERPWalletTransactionSerializer

    def get_queryset(self):
        qs = ERPWalletTransaction.objects.all()
        wallet_id = self.request.query_params.get('wallet')
        if wallet_id:
            qs = qs.filter(wallet_id=wallet_id)
        return qs


class ERPWalletTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPWalletTransaction.objects.all()
    serializer_class = ERPWalletTransactionSerializer


class ERPWalletTransactionCreateView(generics.CreateAPIView):
    """
    Commission withdrawal:
    - Minimum 1000 taka
    - Loan balance deducted first
    """
    queryset = ERPWalletTransaction.objects.all()
    serializer_class = ERPWalletTransactionSerializer

    def create(self, request, *args, **kwargs):
        transaction_type = request.data.get('transaction_type')
        amount = float(request.data.get('amount', 0))

        if transaction_type == 'withdrawal':
            if amount < 1000:
                return Response(
                    {'error': 'Minimum withdrawal amount is 1000 taka.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            wallet_id = request.data.get('wallet')
            if wallet_id:
                wallet = ERPWallet.objects.filter(id=wallet_id).first()
                if wallet and wallet.loan_balance > 0:
                    deduction = min(wallet.loan_balance, amount)
                    wallet.loan_balance -= deduction
                    amount -= deduction
                    wallet.save()
                    if amount <= 0:
                        return Response(
                            {'error': 'No withdrawable amount after loan deduction.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = serializer.save()
        wallet = txn.wallet
        if txn.transaction_type == 'withdrawal':
            wallet.balance -= txn.amount
        else:
            wallet.balance += txn.amount
        wallet.save()
        return Response(self.get_serializer(txn).data, status=status.HTTP_201_CREATED)


# =====================================================
# 14. COMMISSION VIEWS
# =====================================================

class CommissionRuleListCreateView(generics.ListCreateAPIView):
    queryset = ERPCommissionRule.objects.all()
    serializer_class = ERPCommissionRuleSerializer


class CommissionRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPCommissionRule.objects.all()
    serializer_class = ERPCommissionRuleSerializer


class CommissionListView(generics.ListAPIView):
    serializer_class = ERPCommissionSerializer

    def get_queryset(self):
        qs = ERPCommission.objects.all()
        officer = self.request.query_params.get('officer')
        comm_status = self.request.query_params.get('status')
        booking = self.request.query_params.get('booking')
        if officer:
            qs = qs.filter(marketing_officer_id=officer)
        if comm_status:
            qs = qs.filter(status=comm_status)
        if booking:
            qs = qs.filter(booking_id=booking)
        return qs


class CommissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPCommission.objects.all()
    serializer_class = ERPCommissionSerializer

# =====================================================
# ✅ FIXED: GenerateCommissionView
# ====================================================



class GenerateCommissionView(APIView):
    """
    POST /api/generate-commission/

    একটি payment হলে এই endpoint call করলে
    পুরো upline chain এ commission তৈরি হবে এবং
    wallet এ টাকা credit হবে।

    Request Body:
    {
        "booking":     5,            ← ERPBooking এর id (required)
        "amount":      25000,        ← যত টাকা payment হয়েছে (required)
        "source_type": "booking",    ← payment এর ধরন (required)
        "receipt":     12            ← ERPMoneyReceipt এর id (optional)
    }

    source_type এর মান হতে পারে:
        booking / installment / down_payment / investment /
        registration / land_dev / parking / transfer / utility

    Response:
    {
        "message": "3 commission(s) generated successfully",
        "commissions_created": 3,
        "details": [
            {
                "officer": "Rahim",
                "generation": 0,
                "generation_label": "Direct",
                "source_type": "booking",
                "rate": "25.000",
                "base_amount": "25000.00",
                "commission_amount": "6250.00",
                "status": "paid"
            },
            ...
        ]
    }
    """


    def post(self, request):
        # ---- Input নেওয়া ----
        booking_id  = request.data.get('booking')
        amount      = request.data.get('amount')
        source_type = request.data.get('source_type')
        receipt_id  = request.data.get('receipt')   # optional

        # ---- Required field validation ----
        if not booking_id:
            return Response(
                {"error": "'booking' field required. ERPBooking এর id দিন।"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not amount:
            return Response(
                {"error": "'amount' field required। payment এর পরিমাণ দিন।"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not source_type:
            return Response(
                {"error": "'source_type' field required। booking/installment/down_payment ইত্যাদি দিন।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # source_type validation
        valid_sources = [
            'booking', 'installment', 'down_payment', 'investment',
            'registration', 'land_dev', 'parking', 'transfer', 'utility',
        ]
        if source_type not in valid_sources:
            return Response(
                {"error": f"'source_type' অবশ্যই এগুলোর একটি হতে হবে: {', '.join(valid_sources)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---- Booking খোঁজা ----
        try:
            booking = ERPBooking.objects.select_related(
                'marketing_officer',
                'marketing_officer__user',
                'marketing_officer__upline',
                'project',
            ).get(id=booking_id)
        except ERPBooking.DoesNotExist:
            return Response(
                {"error": f"Booking id={booking_id} পাওয়া যায়নি।"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ---- Marketing Officer আছে কিনা চেক ----
        if not booking.marketing_officer:
            return Response(
                {"error": f"Booking '{booking.booking_code}' এ কোনো Marketing Officer নেই। Commission দেওয়া সম্ভব নয়।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---- Receipt খোঁজা (optional) ----
        receipt = None
        if receipt_id:
            try:
                receipt = ERPMoneyReceipt.objects.get(id=receipt_id)
            except ERPMoneyReceipt.DoesNotExist:
                # receipt না পেলেও commission চলবে, শুধু warning দেওয়া হবে
                pass

        # ---- Commission Generate করা ----
        try:
            from mainapp.services import generate_commission
            commissions = generate_commission(
                booking=booking,
                amount=amount,
                source_type=source_type,
                receipt=receipt,
            )
        except Exception as e:
            return Response(
                {"error": f"Commission generate করতে সমস্যা হয়েছে: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ---- Response তৈরি করা ----
        # প্রতিটি commission এর detail response এ দেখানো
        details = []
        for comm in commissions:
            gen_label = "Direct (Shaki)" if comm.generation == 0 else f"{comm.generation}st/nd/rd/th Gen"
            # সঠিক ordinal suffix
            gen_num = comm.generation
            if gen_num == 0:
                gen_label = "Direct (Shaki)"
            elif gen_num == 1:
                gen_label = "1st"
            elif gen_num == 2:
                gen_label = "2nd"
            elif gen_num == 3:
                gen_label = "3rd"
            else:
                gen_label = f"{gen_num}th"

            details.append({
                "officer":           comm.marketing_officer.user.full_name,
                "officer_code":      comm.marketing_officer.officer_code,
                "generation":        comm.generation,
                "generation_label":  gen_label,
                "source_type":       comm.source_type,
                "rate":              str(comm.commission_rate),
                "base_amount":       str(comm.base_amount),
                "commission_amount": str(comm.commission_amount),
                "status":            comm.status,
                "wallet_hit":        comm.wallet_hit,
            })

        if not commissions:
            return Response({
                "message": "কোনো Commission তৈরি হয়নি। Commission Rule না থাকলে অথবা amount 0 হলে এটি হতে পারে।",
                "commissions_created": 0,
                "details": [],
                "hint": f"project={booking.project_id}, source_type={source_type} এর জন্য ERPCommissionRule আছে কিনা চেক করুন।"
            }, status=status.HTTP_200_OK)

        return Response({
            "message":            f"{len(commissions)} commission(s) generated successfully",
            "commissions_created": len(commissions),
            "booking_code":       booking.booking_code,
            "source_type":        source_type,
            "total_amount_paid":  str(amount),
            "details":            details,
        }, status=status.HTTP_201_CREATED)


# =====================================================
# 14B. COMMISSION DASHBOARD
# =====================================================



@api_view(['GET'])
def commission_dashboard(request):
    """
    GET /api/commission-dashboard/

    স্ক্রিনশটের মতো Generation × Source-Type টেবিল।

    Optional Query Params:
        ?project=<id>
        ?officer=<id>
        ?date_from=YYYY-MM-DD
        ?date_to=YYYY-MM-DD
    """
    project_id = request.query_params.get('project')
    officer_id = request.query_params.get('officer')
    date_from  = request.query_params.get('date_from')
    date_to    = request.query_params.get('date_to')

    qs = ERPCommission.objects.all()

    if project_id:
        qs = qs.filter(booking__project_id=project_id)
    if officer_id:
        qs = qs.filter(marketing_officer_id=officer_id)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    SOURCE_TYPES = [
        'booking', 'installment', 'down_payment', 'investment',
        'registration', 'land_dev', 'parking', 'transfer', 'utility',
    ]

    GENERATION_LABELS = {
        0: 'Direct (Shaki)',
        1: '1st',
        2: '2nd',
        3: '3rd',
        4: '4th',
        5: '5th',
        6: '6th',
        7: '7th',
    }

    # Overall Summary
    summary_agg = qs.aggregate(
        total_commission=Sum('commission_amount'),
        total_paid=Sum('commission_amount', filter=Q(status='paid')),
        total_pending=Sum('commission_amount', filter=Q(status__in=['pending', 'approved'])),
        total_officers=Count('marketing_officer', distinct=True),
    )

    # Generation-wise breakdown
    by_generation = []
    column_totals = {src: Decimal('0.00') for src in SOURCE_TYPES}
    grand_total   = Decimal('0.00')

    for gen in range(0, 8):
        row = {
            'generation':       gen,
            'generation_label': GENERATION_LABELS.get(gen, f'Gen {gen}'),
        }
        row_total = Decimal('0.00')

        for source in SOURCE_TYPES:
            agg = qs.filter(
                generation=gen,
                source_type=source
            ).aggregate(
                total_amount=Sum('commission_amount'),
                total_rate=Sum('commission_rate'),
            )

            amount = agg['total_amount'] or Decimal('0.00')
            rate   = agg['total_rate']   or Decimal('0.000')

            row[source] = {
                'percent': float(rate),
                'amount':  float(amount),
            }

            row_total             += amount
            column_totals[source] += amount

        row['row_total'] = float(row_total)
        grand_total      += row_total
        by_generation.append(row)

    column_totals_response = {
        src: {'amount': float(column_totals[src])}
        for src in SOURCE_TYPES
    }
    column_totals_response['grand_total'] = {'amount': float(grand_total)}

    return Response({
        'summary': {
            'total_commission': float(summary_agg['total_commission'] or 0),
            'total_paid':       float(summary_agg['total_paid']       or 0),
            'total_pending':    float(summary_agg['total_pending']     or 0),
            'total_officers':   summary_agg['total_officers']          or 0,
        },
        'by_generation':  by_generation,
        'column_totals':  column_totals_response,
    })


@api_view(['GET'])
def officer_commission_detail(request, officer_id):
    """
    GET /api/commission-dashboard/officer/<officer_id>/
    একজন নির্দিষ্ট officer এর commission detail।
    """
    try:
        officer = ERPMarketingOfficer.objects.select_related('user').get(id=officer_id)
    except ERPMarketingOfficer.DoesNotExist:
        return Response({'error': 'Officer not found'}, status=404)

    commissions = ERPCommission.objects.filter(marketing_officer=officer)

    gen_summary = {}
    for comm in commissions:
        gen = comm.generation
        if gen not in gen_summary:
            gen_summary[gen] = {
                'generation':       gen,
                'label':            'Direct' if gen == 0 else f'Gen {gen}',
                'count':            0,
                'total_amount':     Decimal('0.00'),
                'paid_amount':      Decimal('0.00'),
                'pending_amount':   Decimal('0.00'),
            }
        gen_summary[gen]['count']        += 1
        gen_summary[gen]['total_amount'] += comm.commission_amount
        if comm.status == 'paid':
            gen_summary[gen]['paid_amount']    += comm.commission_amount
        else:
            gen_summary[gen]['pending_amount'] += comm.commission_amount

    gen_list = []
    for gen, data in sorted(gen_summary.items()):
        gen_list.append({
            **data,
            'total_amount':   float(data['total_amount']),
            'paid_amount':    float(data['paid_amount']),
            'pending_amount': float(data['pending_amount']),
        })

    overall = commissions.aggregate(
        total=Sum('commission_amount'),
        paid=Sum('commission_amount', filter=Q(status='paid')),
    )

    wallet_balance = 0
    try:
        wallet_balance = float(officer.user.wallet.balance)
    except Exception:
        pass

    return Response({
        'officer': {
            'id':             officer.id,
            'name':           officer.user.full_name,
            'code':           officer.officer_code,
            'rank':           officer.get_rank_display(),
            'wallet_balance': wallet_balance,
        },
        'commission_summary': {
            'total':   float(overall['total'] or 0),
            'paid':    float(overall['paid']   or 0),
            'pending': float((overall['total'] or 0) - (overall['paid'] or 0)),
        },
        'by_generation': gen_list,
    })


# =====================================================
# 15. LOAN VIEWS
# =====================================================

class ERPLoanListView(generics.ListAPIView):
    """GET /api/erp-loans/ — ?user=<id>"""
    serializer_class = ERPLoanSerializer

    def get_queryset(self):
        qs = ERPLoan.objects.all()
        user_id = self.request.query_params.get('user')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class ERPLoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPLoan.objects.all()
    serializer_class = ERPLoanSerializer


class ERPLoanCreateView(generics.CreateAPIView):
    queryset = ERPLoan.objects.all()
    serializer_class = ERPLoanSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save()
        wallet = ERPWallet.objects.filter(user_id=loan.user_id).first()
        if wallet:
            wallet.loan_balance += loan.loan_amount
            wallet.save()
        return Response(self.get_serializer(loan).data, status=status.HTTP_201_CREATED)


# =====================================================
# 16. INVESTOR VIEWS
# =====================================================

class ERPInvestorListView(generics.ListAPIView):
    queryset = ERPInvestor.objects.all()
    serializer_class = ERPInvestorSerializer


class ERPInvestorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPInvestor.objects.all()
    serializer_class = ERPInvestorSerializer


class ERPInvestorCreateView(generics.CreateAPIView):
    queryset = ERPInvestor.objects.all()
    serializer_class = ERPInvestorSerializer


class ERPInvestmentListView(generics.ListAPIView):
    """GET /api/erp-investments/ — ?investor=<id>&status=<status>"""
    serializer_class = ERPInvestmentSerializer

    def get_queryset(self):
        qs = ERPInvestment.objects.all()
        investor_id = self.request.query_params.get('investor')
        inv_status  = self.request.query_params.get('status')
        if investor_id:
            qs = qs.filter(investor_id=investor_id)
        if inv_status:
            qs = qs.filter(status=inv_status)
        return qs


class ERPInvestmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPInvestment.objects.all()
    serializer_class = ERPInvestmentSerializer


class ERPInvestmentCreateView(generics.CreateAPIView):
    queryset = ERPInvestment.objects.all()
    serializer_class = ERPInvestmentSerializer


class ERPDividendListView(generics.ListAPIView):
    """GET /api/erp-dividends/ — ?investor=<id>&investment=<id>"""
    serializer_class = ERPDividendSerializer

    def get_queryset(self):
        qs = ERPDividend.objects.all()
        investor_id   = self.request.query_params.get('investor')
        investment_id = self.request.query_params.get('investment')
        if investor_id:
            qs = qs.filter(investor_id=investor_id)
        if investment_id:
            qs = qs.filter(investment_id=investment_id)
        return qs


class ERPDividendDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPDividend.objects.all()
    serializer_class = ERPDividendSerializer


from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone as tz


class ERPDividendCreateView(generics.CreateAPIView):
    queryset = ERPDividend.objects.all()
    serializer_class = ERPDividendSerializer

    def create(self, request, *args, **kwargs):
        investment_id = request.data.get('investment')
        month         = request.data.get('month')
        year          = request.data.get('year')

        if not all([investment_id, month, year]):
            return Response(
                {"error": "investment, month, and year are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            investment = ERPInvestment.objects.select_related('investor__user').get(id=investment_id)

            base_amount     = Decimal(str(investment.invest_amount))
            rate_percent    = Decimal(str(investment.monthly_dividend_rate))
            dividend_amount = (base_amount * rate_percent / Decimal('100')).quantize(
                Decimal('0.00'), rounding=ROUND_HALF_UP
            )

            with transaction.atomic():
                wallet = ERPWallet.objects.select_for_update().get(
                    user=investment.investor.user,
                    wallet_type='investor'
                )

                dividend = ERPDividend.objects.create(
                    investment=investment,
                    investor=investment.investor,
                    month=month,
                    year=year,
                    base_amount=base_amount,
                    dividend_rate=rate_percent,
                    dividend_amount=dividend_amount,
                    status='paid',
                    wallet_credited=True,
                    wallet_credited_at=tz.now()
                )

                wallet.balance += dividend_amount
                wallet.save()

                investment.total_profit_received += dividend_amount
                investment.save()

            return Response(self.get_serializer(dividend).data, status=status.HTTP_201_CREATED)

        except ERPInvestment.DoesNotExist:
            return Response({"error": "Investment not found"}, status=404)
        except ERPWallet.DoesNotExist:
            return Response({"error": "Investor wallet not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# =====================================================
# 17. HR VIEWS
# =====================================================

class ERPEmployeeListView(generics.ListAPIView):
    queryset = ERPEmployee.objects.filter(is_active=True)
    serializer_class = ERPEmployeeSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPEmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPEmployee.objects.all()
    serializer_class = ERPEmployeeSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPEmployeeCreateView(generics.CreateAPIView):
    queryset = ERPEmployee.objects.all()
    serializer_class = ERPEmployeeSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPAttendanceListView(generics.ListAPIView):
    """GET /api/erp-attendance/ — ?employee=<id>&month=<m>&year=<y>"""
    serializer_class = ERPAttendanceSerializer

    def get_queryset(self):
        qs = ERPAttendance.objects.all()
        employee_id = self.request.query_params.get('employee')
        month       = self.request.query_params.get('month')
        year        = self.request.query_params.get('year')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if month and year:
            qs = qs.filter(attendance_date__month=month, attendance_date__year=year)
        return qs


class ERPAttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPAttendance.objects.all()
    serializer_class = ERPAttendanceSerializer


class ERPAttendanceCreateView(generics.CreateAPIView):
    queryset = ERPAttendance.objects.all()
    serializer_class = ERPAttendanceSerializer


class ERPPayrollListView(generics.ListAPIView):
    """GET /api/erp-payroll/ — ?employee=<id>&month=<m>&year=<y>"""
    serializer_class = ERPPayrollSerializer

    def get_queryset(self):
        qs = ERPPayroll.objects.all()
        employee_id = self.request.query_params.get('employee')
        month       = self.request.query_params.get('month')
        year        = self.request.query_params.get('year')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)
        return qs


class ERPPayrollDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPPayroll.objects.all()
    serializer_class = ERPPayrollSerializer


class ERPPayrollCreateView(generics.CreateAPIView):
    queryset = ERPPayroll.objects.all()
    serializer_class = ERPPayrollSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payroll = serializer.save()

        attendance_count = ERPAttendance.objects.filter(
            employee_id=payroll.employee_id,
            attendance_date__month=payroll.month,
            attendance_date__year=payroll.year,
            status__in=['present', 'late', 'half_day']
        ).count()

        payroll.present_days  = attendance_count
        working_days          = payroll.working_days or 26
        daily_rate            = float(payroll.basic_salary) / working_days
        payroll.payable_salary = round(daily_rate * attendance_count, 2)
        payroll.net_salary    = payroll.payable_salary - float(payroll.loan_deduction)
        payroll.save()
        return Response(self.get_serializer(payroll).data, status=status.HTTP_201_CREATED)





# =====================================================
# 18. OFFICER REQUEST VIEWS
# =====================================================

class ERPOfficerRequestListView(generics.ListAPIView):
    """GET /api/erp-officer-requests/ — ?officer=<id>&status=<status>&type=<type>"""
    serializer_class = ERPOfficerRequestSerializer

    def get_queryset(self):
        qs = ERPOfficerRequest.objects.all()
        officer_id  = self.request.query_params.get('officer')
        req_status  = self.request.query_params.get('status')
        req_type    = self.request.query_params.get('type')
        if officer_id:
            qs = qs.filter(officer_id=officer_id)
        if req_status:
            qs = qs.filter(status=req_status)
        if req_type:
            qs = qs.filter(request_type=req_type)
        return qs


class ERPOfficerRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPOfficerRequest.objects.all()
    serializer_class = ERPOfficerRequestSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.data.get('status') == 'approved':
            instance.approved_by = request.data.get('approved_by', '')
            instance.approved_at = datetime.now()
            instance.save()
        serializer.save()
        return Response(self.get_serializer(instance).data)


class ERPOfficerRequestCreateView(generics.CreateAPIView):
    queryset = ERPOfficerRequest.objects.all()
    serializer_class = ERPOfficerRequestSerializer

    def create(self, request, *args, **kwargs):
        req_type = request.data.get('request_type')
        amount   = float(request.data.get('amount', 0))
        if req_type == 'commission_withdrawal' and amount < 1000:
            return Response(
                {'error': 'Minimum 1000 taka required for commission withdrawal.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# =====================================================
# 19. ACCOUNT HEAD VIEWS
# =====================================================

class ERPAccountHeadListView(generics.ListAPIView):
    queryset = ERPAccountHead.objects.filter(is_active=True)
    serializer_class = ERPAccountHeadSerializer


class ERPAccountHeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPAccountHead.objects.all()
    serializer_class = ERPAccountHeadSerializer


class ERPAccountHeadCreateView(generics.CreateAPIView):
    queryset = ERPAccountHead.objects.all()
    serializer_class = ERPAccountHeadSerializer


# =====================================================
# 20. OFFER & DISCOUNT VIEWS
# =====================================================

class ERPOfferListView(generics.ListAPIView):
    serializer_class = ERPOfferSerializer

    def get_queryset(self):
        qs = ERPOffer.objects.all()
        project_id  = self.request.query_params.get('project')
        active_only = self.request.query_params.get('active')
        if project_id:
            qs = qs.filter(project_id=project_id)
        if active_only == 'true':
            qs = qs.filter(is_active=True, valid_to__gte=date.today())
        return qs


class ERPOfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPOffer.objects.all()
    serializer_class = ERPOfferSerializer


class ERPOfferCreateView(generics.CreateAPIView):
    queryset = ERPOffer.objects.all()
    serializer_class = ERPOfferSerializer

    def create(self, request, *args, **kwargs):
        valid_from = request.data.get('valid_from')
        valid_to   = request.data.get('valid_to')
        if valid_from and valid_to:
            from_date = date.fromisoformat(valid_from)
            to_date   = date.fromisoformat(valid_to)
            if (to_date - from_date).days > 90:
                return Response(
                    {'error': 'Offer duration cannot exceed 90 days.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# =====================================================
# 21. SMS LOG VIEWS
# =====================================================

class ERPSMSLogListView(generics.ListAPIView):
    serializer_class = ERPSMSLogSerializer

    def get_queryset(self):
        qs = ERPSMSLog.objects.all()
        customer_id = self.request.query_params.get('customer')
        sms_type    = self.request.query_params.get('type')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if sms_type:
            qs = qs.filter(sms_type=sms_type)
        return qs


class ERPSMSLogDetailView(generics.RetrieveAPIView):
    queryset = ERPSMSLog.objects.all()
    serializer_class = ERPSMSLogSerializer


class ERPSMSLogCreateView(generics.CreateAPIView):
    queryset = ERPSMSLog.objects.all()
    serializer_class = ERPSMSLogSerializer


# =====================================================
# 22. DOCUMENT VIEWS
# =====================================================

class ERPDocumentListView(generics.ListAPIView):
    serializer_class = ERPDocumentSerializer

    def get_queryset(self):
        qs = ERPDocumentSerializer
        qs = ERPDocument.objects.all()
        booking_id = self.request.query_params.get('booking')
        doc_type   = self.request.query_params.get('type')
        if booking_id:
            qs = qs.filter(booking_id=booking_id)
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        return qs


class ERPDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPDocument.objects.all()
    serializer_class = ERPDocumentSerializer


class ERPDocumentCreateView(generics.CreateAPIView):
    queryset = ERPDocument.objects.all()
    serializer_class = ERPDocumentSerializer


# =====================================================
# 23. COMPANY ASSET VIEWS
# =====================================================

class ERPCompanyAssetListView(generics.ListAPIView):
    serializer_class = ERPCompanyAssetSerializer

    def get_queryset(self):
        qs = ERPCompanyAsset.objects.all()
        user_id = self.request.query_params.get('assigned_to')
        if user_id:
            qs = qs.filter(assigned_to_id=user_id)
        return qs


class ERPCompanyAssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPCompanyAsset.objects.all()
    serializer_class = ERPCompanyAssetSerializer


class ERPCompanyAssetCreateView(generics.CreateAPIView):
    queryset = ERPCompanyAsset.objects.all()
    serializer_class = ERPCompanyAssetSerializer


# =====================================================
# 24. SYSTEM LOG VIEWS
# =====================================================

class ERPSystemLogListView(generics.ListAPIView):
    queryset = ERPSystemLog.objects.all()
    serializer_class = ERPSystemLogSerializer


class ERPSystemLogCreateView(generics.CreateAPIView):
    queryset = ERPSystemLog.objects.all()
    serializer_class = ERPSystemLogSerializer


# =====================================================
# DASHBOARD SUMMARY API
# =====================================================

@api_view(['GET'])
def erp_dashboard_summary(request):
    """GET /api/erp-dashboard/ — Admin dashboard summary."""
    today          = date.today()
    start_of_month = today.replace(day=1)

    total_bookings    = ERPBooking.objects.count()
    active_bookings   = ERPBooking.objects.filter(status__in=['pending', 'confirmed', 'agreement_done']).count()
    cancelled_bookings = ERPBooking.objects.filter(status='cancelled').count()

    month_receipts = ERPMoneyReceipt.objects.filter(
        payment_date__gte=start_of_month, status='authorized'
    ).aggregate(total=Sum('amount'))['total'] or 0

    today_receipts = ERPMoneyReceipt.objects.filter(
        payment_date=today, status='authorized'
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_receipts = ERPMoneyReceipt.objects.filter(status='pending').count()

    total_plots     = ERPPlot.objects.count()
    available_plots = ERPPlot.objects.filter(status='available').count()
    booked_plots    = ERPPlot.objects.filter(status='booked').count()
    sold_plots      = ERPPlot.objects.filter(status='sold').count()

    upcoming_due = ERPInstallmentPlan.objects.filter(
        is_paid=False,
        due_date__lte=today + timedelta(days=7),
        due_date__gte=today
    ).count()

    total_leads     = ERPLead.objects.count()
    new_leads       = ERPLead.objects.filter(status='new').count()
    converted_leads = ERPLead.objects.filter(status='converted').count()

    total_customers = ERPCustomer.objects.filter(is_active=True).count()
    total_investors = ERPInvestor.objects.filter(is_active=True).count()
    total_marketing = ERPMarketingOfficer.objects.filter(is_active=True).count()

    cheque_expiry_warning = ERPMoneyReceipt.objects.filter(
        payment_mode='cheque',
        cheque_cleared=False,
        cheque_date__lte=today - timedelta(days=25)
    ).count()

    token_expiry_soon = ERPBooking.objects.filter(
        token_status='active',
        token_expiry_date__lte=today + timedelta(days=2),
        token_expiry_date__gte=today
    ).count()

    return Response({
        'today': str(today),
        'bookings': {
            'total':     total_bookings,
            'active':    active_bookings,
            'cancelled': cancelled_bookings,
        },
        'revenue': {
            'today':      float(today_receipts),
            'this_month': float(month_receipts),
        },
        'receipts': {
            'pending_approval': pending_receipts,
        },
        'plots': {
            'total':     total_plots,
            'available': available_plots,
            'booked':    booked_plots,
            'sold':      sold_plots,
        },
        'installments': {
            'due_in_7_days': upcoming_due,
        },
        'leads': {
            'total':     total_leads,
            'new':       new_leads,
            'converted': converted_leads,
        },
        'people': {
            'customers':          total_customers,
            'investors':          total_investors,
            'marketing_officers': total_marketing,
        },
        'alerts': {
            'cheque_expiry_warning': cheque_expiry_warning,
            'token_expiry_soon':     token_expiry_soon,
        },
    })