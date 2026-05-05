# api/views.py
# Real Estate ERP — Complete views based on models.py and serializers.py

from django.contrib.auth.hashers import make_password, check_password
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Sum, Count
from datetime import datetime, date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [AllowAny] # আগের সেই ৪০১ এরর ঠিক করার জন্য

    # আলাদা করে create মেথড লেখার দরকার নেই, 
    # এটি স্বয়ংক্রিয়ভাবে সিরিয়ালাইজারের create() কে কল করবে।


@api_view(['POST'])
@permission_classes([AllowAny])
def erp_user_login(request):
    """
    POST /api/erp-users/login/
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # 1. Validate Input
    if not username or not password:
        return Response(
            {'success': False, 'message': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 2. Find User
        user = ERPUser.objects.get(username=username)
        
        # 3. Check Password
        if check_password(password, user.password_hash):
            if not user.is_active:
                return Response(
                    {'success': False, 'message': 'Account is deactivated'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 4. Update Last Login (Avoid running full save logic if possible)
            user.last_login = datetime.now()
            user.save(update_fields=['last_login'])

            # 5. Generate JWT Tokens
            refresh = RefreshToken.for_user(user)
            
            # 6. Construct Final Response
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
        return ERPUser.objects.filter(role=self.kwargs['role'], is_active=True)


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
        # জোরপূর্বক ইজ অ্যাক্টিভ ট্রু করে সেভ করা
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
    """A lead can only be assigned to one officer (enforced by FK in model)."""
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
        
        # আপডেট সেভ করা
        booking = serializer.save()

        # যদি ডাউন পেমেন্ট আপডেট হয় তবে কিস্তি পুনরায় হিসাব করা
        if 'down_payment_amount' in request.data:
            self._recalculate_installments(booking)
            # রিক্যালকুলেশনের পর ডাটাবেস থেকে লেটেস্ট অবজেক্ট রিফ্রেশ করা
            booking.refresh_from_db()

        return Response(self.get_serializer(booking).data)

    def _recalculate_installments(self, booking):
        # installment_plan যদি related_name হয় তবেই এটি কাজ করবে
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
        
        # ডাটাবেসে সেভ করা (মডেলের save() মেথড কল হবে এবং pricing ক্যালকুলেট হবে)
        booking = serializer.save()
        
        # প্লটের স্ট্যাটাস আপডেট করা
        if booking.plot:
            booking.plot.status = 'booked'
            booking.plot.save()
            
        # রেসপন্স পাঠানোর সময় নতুন ক্যালকুলেটেড ডাটা সহ পাঠানো
        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)


# =====================================================
# 8. INSTALLMENT PLAN VIEWS
# =====================================================

# class ERPInstallmentPlanListView(generics.ListAPIView):
#     """GET /api/erp-installments/ — ?booking=<id>"""
#     serializer_class = ERPInstallmentPlanSerializer

#     def get_queryset(self):
#         qs = ERPInstallmentPlan.objects.all()
#         booking_id = self.request.query_params.get('booking')
#         if booking_id:
#             qs = qs.filter(booking_id=booking_id)
#         return qs


# class ERPInstallmentPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ERPInstallmentPlan.objects.all()
#     serializer_class = ERPInstallmentPlanSerializer


from dateutil.relativedelta import relativedelta
from decimal import Decimal

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
        # URL থেকে booking_code সংগ্রহ করা হচ্ছে
        booking_code = self.kwargs['booking_code']
        # ওই বুকিং কোড অনুযায়ী কিস্তিগুলো ফিল্টার করা
        return ERPInstallmentPlan.objects.filter(booking__booking_code=booking_code)
    
    
class ERPInstallmentUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ERPInstallmentPlan.objects.all()
    serializer_class = ERPInstallmentPlanSerializer
    


class ERPGenerateInstallmentScheduleView(generics.GenericAPIView):
    """
    booking_code ব্যবহার করে পুরো কিস্তি শিডিউল জেনারেট করার লজিক।
    Input: booking_code, number_of_installments, start_date
    """
    def post(self, request):
        # এখন আমরা booking_id এর বদলে booking_code নিচ্ছি
        booking_code = request.data.get('booking_code')
        num_inst_raw = request.data.get('number_of_installments')
        start_date_str = request.data.get('start_date')

        # বেসিক ভ্যালিডেশন
        if not all([booking_code, num_inst_raw, start_date_str]):
            return Response(
                {"error": "booking_code, number_of_installments and start_date are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .models import ERPBooking, ERPInstallmentPlan
            num_inst = int(num_inst_raw)
            
            # booking_code দিয়ে অবজেক্টটি খুঁজে বের করা
            try:
                booking = ERPBooking.objects.get(booking_code=booking_code)
            except ERPBooking.DoesNotExist:
                return Response({"error": f"Booking with code {booking_code} not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # ১. আগের কোনো শিডিউল থাকলে ডিলিট করা
            booking.installment_plan.all().delete()

            # ২. ক্যালকুলেশন শুরু
            total_to_distribute = booking.total_due
            
            if total_to_distribute <= 0:
                return Response({"error": "Total due is 0. No installments needed."}, status=status.HTTP_400_BAD_REQUEST)

            amount_per_inst = round(total_to_distribute / num_inst, 2)
            current_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            installments = []
            cumulative_amount = Decimal('0.00')

            # ৩. লুপ চালিয়ে কিস্তি তৈরি
            for i in range(1, num_inst + 1):
                if i == num_inst:
                    # শেষ কিস্তিতে পয়সার রাউন্ডিং অ্যাডজাস্ট করা
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
                # প্রতি কিস্তিতে ১ মাস বৃদ্ধি
                current_date += relativedelta(months=1)

            # ৪. Bulk Create ব্যবহার করে একবারে সেভ করা
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
from datetime import datetime
from rest_framework import generics, status
from rest_framework.response import Response

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
                inst.paid_date = receipt.payment_date
            inst.save()



class ERPMoneyReceiptCreateView(generics.CreateAPIView):
    queryset = ERPMoneyReceipt.objects.all()
    serializer_class = ERPMoneyReceiptSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receipt = serializer.save()

        # কমিশন ট্রিগার লজিক
        if receipt.payment_mode == 'cash' and receipt.status == 'authorized':
            self._trigger_commission(receipt)

        # রেসপন্স ডাটা তৈরি
        data = self.get_serializer(receipt).data
        
        # যদি সাথে সাথে PDF ডাউনলোড করতে চান, তবে আলাদা URL ব্যবহার করা ভালো। 
        # তবে ক্রিয়েট করার সময় শুধু ডাটা রিটার্ন করাই স্ট্যান্ডার্ড।
        return Response(data, status=status.HTTP_201_CREATED)

    def _trigger_commission(self, receipt):
        booking = receipt.booking
        if booking and booking.marketing_officer:
            pending_commissions = ERPCommission.objects.filter(
                booking=booking,
                is_cash_payment=True,
                wallet_hit=False
            )
            for commission in pending_commissions:
                commission.wallet_hit = True
                commission.wallet_hit_at = datetime.now()
                commission.status = 'paid'
                commission.save()
                
                wallet = ERPWallet.objects.filter(
                    user=commission.marketing_officer.user
                ).first()
                if wallet:
                    wallet.balance += commission.commission_amount
                    wallet.save()

# PDF জেনারেশনের জন্য আলাদা একটি View রাখা ভালো
class ERPMoneyReceiptDownloadView(generics.RetrieveAPIView):
    queryset = ERPMoneyReceipt.objects.all()

    def get(self, request, *args, **kwargs):
        receipt_obj = self.get_object()
        
        # Amount in Words ডাইনামিক করার জন্য num2words লাইব্রেরি ব্যবহার করতে পারেন
        # অথবা আপনার ম্যানুয়াল ফরম্যাট
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
    """No backdated entry. Auto print on creation."""
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
    """Admin confirms the visit."""
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
    """Marketing officer adds visit; admin confirms. System sends notifications."""
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
    """GET /api/erp-officers/<pk>/downline/ — Team leader sees only their downline."""
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
        transaction = serializer.save()
        wallet = transaction.wallet
        if transaction.transaction_type == 'withdrawal':
            wallet.balance -= transaction.amount
        else:
            wallet.balance += transaction.amount
        wallet.save()
        return Response(self.get_serializer(transaction).data, status=status.HTTP_201_CREATED)


# =====================================================
# 14. COMMISSION VIEWS
# =====================================================

class ERPCommissionRuleListView(generics.ListAPIView):
    """GET /api/erp-commission-rules/ — Management can change."""
    queryset = ERPCommissionRule.objects.filter(is_active=True)
    serializer_class = ERPCommissionRuleSerializer


class ERPCommissionRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPCommissionRule.objects.all()
    serializer_class = ERPCommissionRuleSerializer


class ERPCommissionRuleCreateView(generics.CreateAPIView):
    queryset = ERPCommissionRule.objects.all()
    serializer_class = ERPCommissionRuleSerializer


class ERPCommissionListView(generics.ListAPIView):
    """GET /api/erp-commissions/ — ?officer=<id>&booking=<id>&status=<status>"""
    serializer_class = ERPCommissionSerializer

    def get_queryset(self):
        qs = ERPCommission.objects.all()
        officer_id = self.request.query_params.get('officer')
        booking_id = self.request.query_params.get('booking')
        comm_status = self.request.query_params.get('status')
        if officer_id:
            qs = qs.filter(marketing_officer_id=officer_id)
        if booking_id:
            qs = qs.filter(booking_id=booking_id)
        if comm_status:
            qs = qs.filter(status=comm_status)
        return qs


class ERPCommissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPCommission.objects.all()
    serializer_class = ERPCommissionSerializer


class ERPCommissionCreateView(generics.CreateAPIView):
    """Commission up to 9/10 generations. Cash → wallet immediately. Cheque/bank → after clearing."""
    queryset = ERPCommission.objects.all()
    serializer_class = ERPCommissionSerializer


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
    """Short-term loan — auto-deducted from commission/incentive/salary."""
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
    queryset = ERPInvestor.objects.filter()
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
        inv_status = self.request.query_params.get('status')
        if investor_id:
            qs = qs.filter(investor_id=investor_id)
        if inv_status:
            qs = qs.filter(status=inv_status)
        return qs


class ERPInvestmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Asset transfer between products. Cancellation → phased refund."""
    queryset = ERPInvestment.objects.all()
    serializer_class = ERPInvestmentSerializer


class ERPInvestmentCreateView(generics.CreateAPIView):
    print("arjun")
    queryset = ERPInvestment.objects.all()
    serializer_class = ERPInvestmentSerializer


class ERPDividendListView(generics.ListAPIView):
    """GET /api/erp-dividends/ — ?investor=<id>&investment=<id>"""
    serializer_class = ERPDividendSerializer
    print("arjun")

    def get_queryset(self):
        qs = ERPDividend.objects.all()
        investor_id = self.request.query_params.get('investor')
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
from django.db import transaction
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.response import Response

class ERPDividendCreateView(generics.CreateAPIView):
    queryset = ERPDividend.objects.all()
    serializer_class = ERPDividendSerializer

    def create(self, request, *args, **kwargs):
        investment_id = request.data.get('investment')
        month = request.data.get('month')
        year = request.data.get('year')

        if not all([investment_id, month, year]):
            return Response(
                {"error": "investment, month, and year are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            investment = ERPInvestment.objects.select_related('investor__user').get(id=investment_id)

            # 🚫 Duplicate check
            # if ERPDividend.objects.filter(
            #     investment=investment,
            #     month=month,
            #     year=year
            # ).exists():
            #     return Response(
            #         {"error": "Dividend already created for this month"},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            base_amount = Decimal(str(investment.invest_amount))
            rate_percent = Decimal(str(investment.monthly_dividend_rate))

            # 👉 calculation
            dividend_amount = (
                base_amount * rate_percent / Decimal('100')
            ).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

            with transaction.atomic():

                # 🔐 wallet lock with get()
                wallet = ERPWallet.objects.select_for_update().get(
                    user=investment.investor.user,
                    wallet_type='investor'
                )

                # ✅ create dividend
                dividend = ERPDividend.objects.create(
                    investment=investment,
                    investor=investment.investor,
                    month=month,
                    year=year,
                    base_amount=base_amount,
                    dividend_rate=rate_percent,  # store percent
                    dividend_amount=dividend_amount,
                    status='paid',
                    wallet_credited=True,
                    wallet_credited_at=timezone.now()
                )

                # 💰 wallet update
                wallet.balance += dividend_amount
                wallet.save()

                # 📈 update investment লাভ
                investment.total_profit_received += dividend_amount
                investment.save()

            return Response(
                self.get_serializer(dividend).data,
                status=status.HTTP_201_CREATED
            )

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
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if month and year:
            qs = qs.filter(attendance_date__month=month, attendance_date__year=year)
        return qs


class ERPAttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPAttendance.objects.all()
    serializer_class = ERPAttendanceSerializer


class ERPAttendanceCreateView(generics.CreateAPIView):
    """Data comes from fingerprint device."""
    queryset = ERPAttendance.objects.all()
    serializer_class = ERPAttendanceSerializer


class ERPPayrollListView(generics.ListAPIView):
    """GET /api/erp-payroll/ — ?employee=<id>&month=<m>&year=<y>"""
    serializer_class = ERPPayrollSerializer

    def get_queryset(self):
        qs = ERPPayroll.objects.all()
        employee_id = self.request.query_params.get('employee')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
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
    """Salary calculated based on attendance. Printable at month end."""
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
        payroll.present_days = attendance_count
        working_days = payroll.working_days or 26
        daily_rate = float(payroll.basic_salary) / working_days
        payroll.payable_salary = round(daily_rate * attendance_count, 2)
        payroll.net_salary = payroll.payable_salary - float(payroll.loan_deduction)
        payroll.save()
        return Response(self.get_serializer(payroll).data, status=status.HTTP_201_CREATED)


# =====================================================
# 18. OFFICER REQUEST VIEWS (TA/DA/Commission)
# =====================================================

class ERPOfficerRequestListView(generics.ListAPIView):
    """GET /api/erp-officer-requests/ — ?officer=<id>&status=<status>&type=<type>"""
    serializer_class = ERPOfficerRequestSerializer

    def get_queryset(self):
        qs = ERPOfficerRequest.objects.all()
        officer_id = self.request.query_params.get('officer')
        req_status = self.request.query_params.get('status')
        req_type = self.request.query_params.get('type')
        if officer_id:
            qs = qs.filter(officer_id=officer_id)
        if req_status:
            qs = qs.filter(status=req_status)
        if req_type:
            qs = qs.filter(request_type=req_type)
        return qs


class ERPOfficerRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Accounts/Admin/Department head approves."""
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
    """Officer submits request. Commission withdrawal minimum 1000 taka."""
    queryset = ERPOfficerRequest.objects.all()
    serializer_class = ERPOfficerRequestSerializer

    def create(self, request, *args, **kwargs):
        req_type = request.data.get('request_type')
        amount = float(request.data.get('amount', 0))
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
    """GET /api/erp-offers/ — ?project=<id>&active=true. Max 90 days."""
    serializer_class = ERPOfferSerializer

    def get_queryset(self):
        qs = ERPOffer.objects.all()
        project_id = self.request.query_params.get('project')
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
    """Offer cannot exceed 90 days."""
    queryset = ERPOffer.objects.all()
    serializer_class = ERPOfferSerializer

    def create(self, request, *args, **kwargs):
        valid_from = request.data.get('valid_from')
        valid_to = request.data.get('valid_to')
        if valid_from and valid_to:
            from_date = date.fromisoformat(valid_from)
            to_date = date.fromisoformat(valid_to)
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
    """GET /api/erp-sms-logs/ — ?customer=<id>&type=<type>"""
    serializer_class = ERPSMSLogSerializer

    def get_queryset(self):
        qs = ERPSMSLog.objects.all()
        customer_id = self.request.query_params.get('customer')
        sms_type = self.request.query_params.get('type')
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
    """GET /api/erp-documents/ — ?booking=<id>&type=<type>"""
    serializer_class = ERPDocumentSerializer

    def get_queryset(self):
        qs = ERPDocument.objects.all()
        booking_id = self.request.query_params.get('booking')
        doc_type = self.request.query_params.get('type')
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
# 23. COMPANY ASSET (LOGISTICS) VIEWS
# =====================================================

class ERPCompanyAssetListView(generics.ListAPIView):
    """GET /api/erp-assets/ — ?assigned_to=<user_id>"""
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
    today = date.today()
    start_of_month = today.replace(day=1)

    total_bookings = ERPBooking.objects.count()
    active_bookings = ERPBooking.objects.filter(
        status__in=['pending', 'confirmed', 'agreement_done']
    ).count()
    cancelled_bookings = ERPBooking.objects.filter(status='cancelled').count()

    month_receipts = ERPMoneyReceipt.objects.filter(
        payment_date__gte=start_of_month,
        status='authorized'
    ).aggregate(total=Sum('amount'))['total'] or 0

    today_receipts = ERPMoneyReceipt.objects.filter(
        payment_date=today,
        status='authorized'
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_receipts = ERPMoneyReceipt.objects.filter(status='pending').count()

    total_plots = ERPPlot.objects.count()
    available_plots = ERPPlot.objects.filter(status='available').count()
    booked_plots = ERPPlot.objects.filter(status='booked').count()
    sold_plots = ERPPlot.objects.filter(status='sold').count()

    upcoming_due = ERPInstallmentPlan.objects.filter(
        is_paid=False,
        due_date__lte=today + timedelta(days=7),
        due_date__gte=today
    ).count()

    total_leads = ERPLead.objects.count()
    new_leads = ERPLead.objects.filter(status='new').count()
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
            'total': total_bookings,
            'active': active_bookings,
            'cancelled': cancelled_bookings,
        },
        'revenue': {
            'today': float(today_receipts),
            'this_month': float(month_receipts),
        },
        'receipts': {
            'pending_approval': pending_receipts,
        },
        'plots': {
            'total': total_plots,
            'available': available_plots,
            'booked': booked_plots,
            'sold': sold_plots,
        },
        'installments': {
            'due_in_7_days': upcoming_due,
        },
        'leads': {
            'total': total_leads,
            'new': new_leads,
            'converted': converted_leads,
        },
        'people': {
            'customers': total_customers,
            'investors': total_investors,
            'marketing_officers': total_marketing,
        },
        'alerts': {
            'cheque_expiry_warning': cheque_expiry_warning,
            'token_expiry_soon': token_expiry_soon,
        },
    })