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
from rest_framework import viewsets, filters
from rest_framework.generics import ListAPIView
# views.py এর top এ
from django.db.models import Sum, Count, Q, Avg, F
from django.db import models 

from mainapp.models import (
    ERPUser,
    Project,
    Property,
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
    LandPowerAssignment,
    ERPSupplier, 
    ERPLandOwner, 
    ERPLandAcquisition,
    Transaction,
)

from mainapp.serializers import (
    ERPUserSerializer,
    ERPUserCreateSerializer,
    ERPUserListSerializer,
    ERPProjectSerializer,
    ERPPlotSerializer,
    FeaturedPlotSerializer,
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
    LandPowerAssignmentSerializer,
    ERPSupplierSerializer,
    ERPLandOwnerSerializer,
    ERPLandAcquisitionSerializer,
    TransactionSerializer,
    ERPUserProfileSerializer
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .serializers import ERPUserProfileSerializer # আপনার সিরিয়ালাইজারটি ইমপোর্ট করুন

# আপনার পারমিশন ফাইল থেকে ক্যাশ হেল্পারটি ইমপোর্ট করুন
from accesscontrol.permissions import get_role_permissions 

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.filters import ERPLandAcquisitionFilter, ERPPlotFilter, ERPProjectFilter
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status

from mainapp.api_permissions import (
    HasModulePermission,
    IsCustomer,
    IsInvestor,
    IsEmployee,
    IsMarketingOfficer,
    IsMarketingManager,
    IsAdmin,
    IsSuperAdmin,
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



from .accesscontrol import generate_access_control
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """প্রোফাইল দেখা"""
        user = request.user
        user_data = ERPUserProfileSerializer(user, context={'request': request}).data

        # 🔐 ডাইনামিক এক্সেস কন্ট্রোল জেনারেট করা
        access_control = generate_access_control(user)
        
        # সিরিয়ালাইজড ডাটার ভেতরেই 'access_control' ঢুকিয়ে দেওয়া
        user_data['access_control'] = access_control

        return Response({
            'success': True,
            'data': {
                'user': user_data,
            }
        })

    def patch(self, request):
        """প্রোফাইল আপডেট"""
        user = request.user
        user_serializer = ERPUserProfileSerializer(
            user, data=request.data, partial=True, context={'request': request}
        )

        if not user_serializer.is_valid():
            return Response({
                'success': False,
                'errors': user_serializer.errors
            }, status=400)

        user_serializer.save()
        
        # 🔐 আপডেট হওয়ার পর আবার নতুন করে পারমিশন চেক করা (যদি রোল চেঞ্জ হয়ে থাকে)
        user_data = user_serializer.data
        access_control = generate_access_control(user)
        user_data['access_control'] = access_control

        return Response({
            'success': True,
            'message': 'প্রোফাইল আপডেট সফল হয়েছে।',
            'data': {
                'user': user_data,
            }
        })


class ALLRoleChoicesView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        # ERPUser মডেল থেকে ROLE_CHOICES নিয়ে আসা
        choices = getattr(ERPUser, 'ROLE_CHOICES', [])
        
        # ফ্রন্টএন্ডের সুবিধার জন্য কি-ভ্যালু পেয়ার অবজেক্ট ফরম্যাটে রূপান্তর
        formatted_roles = [{"id": key, "name": value} for key, value in choices]
        
        return Response({
            "success": True,
            "data": formatted_roles
        })
    


from mainapp.log_utils import create_log, get_ip  # ফাইলের উপরে import এ যোগ করো

@api_view(['POST'])
@permission_classes([AllowAny])
def erp_user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            refresh = RefreshToken.for_user(user)
            user_roles = list(user.roles or [])
            access_control = {}

            if 'admin' in user_roles or 'super_admin' in user_roles:
                all_modules = [
                    'project', 'plot', 'booking', 'installment', 'receipt',
                    'commission', 'wallet', 'lead', 'attendance', 'payroll',
                    'investment', 'dividend', 'officer_request', 'document', 'offer'
                ]
                for module in all_modules:
                    access_control[module] = {
                        "view": True, "create": True,
                        "edit": True, "delete": True, "scope": "all"
                    }
            else:
                for role in user_roles:
                    role_perms = get_role_permissions(role)
                    for codename, scope in role_perms.items():
                        if '.' in codename:
                            module, action = codename.split('.', 1)
                        else:
                            continue
                        if module not in access_control:
                            access_control[module] = {
                                "view": False, "create": False,
                                "edit": False, "delete": False, "scope": "own"
                            }
                        if action in access_control[module]:
                            access_control[module][action] = True
                        if scope == 'all':
                            access_control[module]["scope"] = 'all'
                        elif scope == 'own' and access_control[module]["scope"] != 'all':
                            access_control[module]["scope"] = 'own'

            # ✅ Login success log
            create_log(
                action='User Login',
                module='AUTH',
                user=user,
                description=f'{user.username} logged in successfully',
                ip_address=get_ip(request),
                log_level='info',
            )

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'roles': user_roles,
                    'access_control': access_control
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            # ✅ Disabled account log
            create_log(
                action='Login Blocked',
                module='AUTH',
                description=f'{username} account is disabled',
                ip_address=get_ip(request),
                log_level='warning',
            )
            return Response({'error': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)

    else:
        # ✅ Login failed log
        create_log(
            action='Login Failed',
            module='AUTH',
            description=f'Invalid credentials for username: {username}',
            ip_address=get_ip(request),
            log_level='warning',
        )
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)




class ERPUserByRoleView(generics.ListAPIView):
    """GET /api/erp-users/role/<role>/"""
    serializer_class = ERPUserListSerializer

    def get_queryset(self):
        return ERPUser.objects.filter(roles__contains=[self.kwargs['role']], is_active=True)

# =====================================================
# 2. PROJECT VIEWS
# =====================================================


class ERPProjectListView(generics.ListAPIView):
  
    permission_classes = [HasModulePermission]
    permission_module = 'project'    
    queryset = Project.objects.all()
    serializer_class = ERPProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ERPProjectFilter
    search_fields = [
        'project_name',       
        'project_code',       
        'description',        
        'address',            
        'city',               
        'district',           
        'upazila',            
        'mouza',            
    ]
    ordering_fields = [
        'total_project_value',
        'total_land_area',
        'total_plots',
        'available_plots',
        'launch_date',
        'completion_date',
        'created_at',
    ]
    ordering = ['-created_at']  # default ordering


class ERPProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasModulePermission]
    permission_module = 'project'     
    queryset = Project.objects.all()
    serializer_class = ERPProjectSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ERPProjectCreateView(generics.CreateAPIView):
    permission_classes = [HasModulePermission]
    permission_module = 'project' 
    queryset = Project.objects.all()
    serializer_class = ERPProjectSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


# =====================================================
# 3. PLOT / FLAT VIEWS
# =====================================================

class ERPPlotListView(generics.ListAPIView):
    permission_classes = [HasModulePermission]
    permission_module = 'plot'
   
    serializer_class = ERPPlotSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ERPPlotFilter
    search_fields = [
        'plot_number',          
        'notes',               
        'flat_number',          
        'facing',              
        'plot_type',            
        'road',                 
        'building_type',        
        'building_orientation', 
        'area_unit',            
        'project__project_name',
        'project__project_code',
        'project__city',        
        'project__district',    
    ]
    ordering_fields = [
        'final_price',
        'total_price',
        'area',
        'floor_number',
        'plot_number',
        'created_at',
    ]
    ordering = ['plot_number']  # default ordering
 
    def get_queryset(self):
        return Property.objects.select_related('project').all()


class ERPPlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasModulePermission]
    permission_module = 'plot'
    queryset = Property.objects.all()
    serializer_class = ERPPlotSerializer


class ERPPlotCreateView(generics.CreateAPIView):
    permission_classes = [HasModulePermission]
    permission_module = 'plot'
    queryset = Property.objects.all()
    serializer_class = ERPPlotSerializer

class FeaturedPlotListAPIView(ListAPIView):
    permission_classes = [HasModulePermission]
    permission_module = 'plot'
    
    serializer_class = FeaturedPlotSerializer
    def get_queryset(self):
        return Property.objects.filter(
            is_featured=True
        ).order_by('-id')
    

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


# views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from mainapp.models import ERPCustomer
from mainapp.serializers import ERPCustomerSerializer
from mainapp.api_permissions import HasModulePermission


# =====================================================
# LIST
# =====================================================

class ERPCustomerListView(generics.ListAPIView):
    queryset         = ERPCustomer.objects.select_related('user').filter(is_active=True)
    serializer_class = ERPCustomerSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]
    permission_classes  = [HasModulePermission]
    permission_module   = 'customer'

    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'source', 'is_active']
    search_fields    = ['user__full_name', 'user__phone', 'customer_code', 'notes']
    ordering_fields  = ['created_at', 'loyalty_points']
    ordering         = ['-created_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page     = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
            })

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            'success': True,
            'count'  : queryset.count(),
            'data'   : serializer.data,
        })


# =====================================================
# CREATE
# =====================================================

class ERPCustomerCreateView(generics.CreateAPIView):
    queryset            = ERPCustomer.objects.all()
    serializer_class    = ERPCustomerSerializer
    parser_classes      = [MultiPartParser, FormParser, JSONParser]
    permission_classes  = [HasModulePermission]
    permission_module   = 'customer'

    def create(self, request, *args, **kwargs):
        # existing customer check
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({
                'success': False,
                'message': 'user_id দেওয়া আবশ্যক।',
            }, status=status.HTTP_400_BAD_REQUEST)

        if ERPCustomer.objects.filter(user_id=user_id).exists():
            return Response({
                'success': False,
                'message': 'এই user এর জন্য ইতিমধ্যে একটি customer account আছে।',
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': 'Customer সফলভাবে তৈরি হয়েছে।',
                'data'   : serializer.data,
            }, status=status.HTTP_201_CREATED)

        print("ERRORS:", serializer.errors)
        return Response({
            'success': False,
            'errors' : serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(created_by=str(self.request.user))


        
# =====================================================
# DETAIL / UPDATE / DELETE
# =====================================================
class ERPCustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = ERPCustomer.objects.select_related('user').all()
    serializer_class = ERPCustomerSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]
    permission_classes  = [HasModulePermission]
    permission_module   = 'customer'

    def retrieve(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({
            'success': True,
            'data'   : serializer.data,
        })

    def update(self, request, *args, **kwargs):
        partial    = kwargs.pop('partial', False)
        instance   = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data,
            partial=partial,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Customer আপডেট সফল হয়েছে।',
                'data'   : serializer.data,
            })

        return Response({
            'success': False,
            'errors' : serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance          = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response({
            'success': True,
            'message': 'Customer নিষ্ক্রিয় করা হয়েছে।',
        }, status=status.HTTP_200_OK)





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




#======================================================
# TRANACTIONS TABLE
#=====================================================

from mainapp.filters import TransactionFilter

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related(
        'customer', 'project', 'plot',
        'referred_by', 'transferred_to'
    ).all()
    serializer_class = TransactionSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter

    search_fields = [
        'notes',
        'customer__full_name',
        'project__name',
        'referred_by__username',
        'transferred_to__full_name',
    ]

    ordering_fields = ['created_at', 'updated_at', 'amount']
    ordering = ['-created_at']

    # def perform_create(self, serializer):
    #     if not self.request.data.get('referred_by'):
    #         serializer.save(referred_by=self.request.user)
    #     else:
    #         serializer.save()
    def perform_create(self, serializer):
        serializer.save()


#==============================================================
# Commission
#============================================================

# views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from mainapp.models import Commission
from mainapp.serializers import CommissionSerializer


# =====================================================
# COMMISSION LIST
# =====================================================

class CommissionListView(generics.ListAPIView):
    serializer_class   = CommissionSerializer
    permission_classes = [HasModulePermission]
    permission_module  = 'commission'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ── Search — %abc% style ──────────────────────────
    search_fields  = [
        'user__full_name',
        'user__username',
        'user__phone',
        'project__project_name',
        'project__project_code',
        'plot__plot_number',
        'commission_type',
        'note',
    ]

    # ── Ordering ──────────────────────────────────────
    ordering_fields = ['created_at', 'paid_at', 'commission', 'percent', 'level']
    ordering        = ['-created_at']

    def get_queryset(self):
        qs = Commission.objects.select_related('user', 'project', 'plot').all()

        params = self.request.query_params

        # ── Exact filters ─────────────────────────────
        user            = params.get('user')
        project         = params.get('project')
        commission_type = params.get('commission_type')
        paid            = params.get('paid')
        level           = params.get('level')

        if user:            qs = qs.filter(user_id=user)
        if project:         qs = qs.filter(project_id=project)
        if commission_type: qs = qs.filter(commission_type=commission_type)
        if level:           qs = qs.filter(level=level)

        if paid == 'true':  qs = qs.filter(paid_at__isnull=False)
        elif paid == 'false': qs = qs.filter(paid_at__isnull=True)

        # ── Date range filters ────────────────────────
        date_from = params.get('date_from')  # ?date_from=2026-01-01
        date_to   = params.get('date_to')    # ?date_to=2026-05-31

        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        # ── Paid date range ───────────────────────────
        paid_from = params.get('paid_from')  # ?paid_from=2026-01-01
        paid_to   = params.get('paid_to')    # ?paid_to=2026-05-31

        if paid_from:
            qs = qs.filter(paid_at__date__gte=paid_from)
        if paid_to:
            qs = qs.filter(paid_at__date__lte=paid_to)

        # ── Commission amount range ───────────────────
        amount_min = params.get('amount_min')  # ?amount_min=1000
        amount_max = params.get('amount_max')  # ?amount_max=50000

        if amount_min: qs = qs.filter(commission__gte=amount_min)
        if amount_max: qs = qs.filter(commission__lte=amount_max)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page     = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response({
                'success': True,
                'data'   : serializer.data,
            })

        serializer = self.get_serializer(queryset, many=True, context={'request': request})

        # ── Summary ───────────────────────────────────
        from django.db.models import Sum, Count
        summary = queryset.aggregate(
            total_commission = Sum('commission'),
            total_paid       = Sum('commission', filter=models.Q(paid_at__isnull=False)),
            total_unpaid     = Sum('commission', filter=models.Q(paid_at__isnull=True)),
            total_count      = Count('id'),
        )

        return Response({
            'success': True,
            'count'  : queryset.count(),
            'summary': {
                'total_commission': summary['total_commission'] or 0,
                'total_paid'      : summary['total_paid']       or 0,
                'total_unpaid'    : summary['total_unpaid']     or 0,
                'total_count'     : summary['total_count']      or 0,
            },
            'data'   : serializer.data,
        })

class CommissionDetailView(generics.RetrieveAPIView):
    """GET /commissions/<id>/"""
    queryset         = Commission.objects.select_related('user', 'project', 'plot').all()
    serializer_class = CommissionSerializer


class CommissionCreateView(generics.CreateAPIView):
    """POST /commissions/create/"""
    queryset         = Commission.objects.all()
    serializer_class = CommissionSerializer


class CommissionUpdateView(generics.UpdateAPIView):
    """PATCH /commissions/<id>/update/"""
    queryset          = Commission.objects.all()
    serializer_class  = CommissionSerializer
    http_method_names = ['patch']


class CommissionDeleteView(generics.DestroyAPIView):
    """DELETE /commissions/<id>/delete/"""
    queryset         = Commission.objects.all()
    serializer_class = CommissionSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Commission deleted successfully.'})


class CommissionMarkPaidView(generics.UpdateAPIView):
    """
    PATCH /commissions/<id>/mark-paid/
    Commission paid mark করা
    """
    queryset          = Commission.objects.all()
    serializer_class  = CommissionSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        from django.utils import timezone
        instance         = self.get_object()
        instance.paid_at = timezone.now()
        instance.save()
        return Response({
            'message': 'Commission marked as paid.',
            'paid_at': instance.paid_at,
        })


class CommissionSummaryView(generics.ListAPIView):
    """
    GET /commissions/summary/
    প্রতিটি user এর total commission summary
    """
    def get(self, request):
        from django.db.models import Sum, Count, Q

        summary = Commission.objects.values(
            'user__id', 'user__full_name'
        ).annotate(
            total_commission = Sum('commission'),
            total_count      = Count('id'),
            paid_count       = Count('id', filter=Q(paid_at__isnull=False)),
            unpaid_count     = Count('id', filter=Q(paid_at__isnull=True)),
        ).order_by('-total_commission')

        return Response(summary)



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


class ERPInstallmentUpdateView(generics.RetrieveUpdateDestroyAPIView):
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
    serializer_class = ERPVoucherSerializer

    def get_queryset(self):
        # ✅ select_related — N+1 fix
        qs = ERPVoucher.objects.select_related(
            'customer',
            'booking',
            'debit_head',
            'credit_head',
            'approved_by',
            'created_by'
        ).all()

        v_type  = self.request.query_params.get('type')
        status  = self.request.query_params.get('status')
        customer_id = self.request.query_params.get('customer')
        booking_id  = self.request.query_params.get('booking')

        if v_type:
            qs = qs.filter(voucher_type=v_type)
        if status:
            qs = qs.filter(status=status)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if booking_id:
            qs = qs.filter(booking_id=booking_id)

        return qs


class ERPVoucherDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ERPVoucherSerializer

    def get_queryset(self):
        return ERPVoucher.objects.select_related(
            'customer', 'booking',
            'debit_head', 'credit_head',
            'approved_by', 'created_by'
        )

    # ✅ approved voucher delete করা যাবে না
    def destroy(self, request, *args, **kwargs):
        voucher = self.get_object()
        if voucher.status == 'approved':
            return Response(
                {'error': 'Approved voucher cannot be deleted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ERPVoucherCreateView(generics.CreateAPIView):
    serializer_class = ERPVoucherSerializer

    def get_queryset(self):
        return ERPVoucher.objects.select_related(
            'customer', 'booking',
            'debit_head', 'credit_head',
            'approved_by', 'created_by'
        )

    # ✅ voucher_number auto-generate
    def perform_create(self, serializer):
        year = date.today().year
        last = ERPVoucher.objects.filter(
            voucher_number__startswith=f'VCH-{year}-'
        ).count()
        voucher_number = f'VCH-{year}-{str(last + 1).zfill(4)}'
        serializer.save(voucher_number=voucher_number)


# ✅ Approve / Reject এর আলাদা endpoint
class ERPVoucherApproveView(generics.UpdateAPIView):
    serializer_class = ERPVoucherSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return ERPVoucher.objects.all()

    def patch(self, request, *args, **kwargs):
        voucher = self.get_object()

        if voucher.status != 'draft':
            return Response(
                {'error': f'Only draft vouchers can be approved. Current status: {voucher.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        voucher.status = 'approved'
        voucher.approved_by_id = request.data.get('approved_by')
        voucher.approved_at = date.today()
        voucher.save()

        return Response(
            ERPVoucherSerializer(voucher).data,
            status=status.HTTP_200_OK
        )


class ERPVoucherRejectView(generics.UpdateAPIView):
    serializer_class = ERPVoucherSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return ERPVoucher.objects.all()

    def patch(self, request, *args, **kwargs):
        voucher = self.get_object()

        if voucher.status != 'draft':
            return Response(
                {'error': f'Only draft vouchers can be rejected. Current status: {voucher.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        voucher.status = 'rejected'
        voucher.save()

        return Response(
            ERPVoucherSerializer(voucher).data,
            status=status.HTTP_200_OK
        )


# =====================================================
# 11. PROJECT VISIT VIEWS
# =====================================================
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response


class ERPProjectVisitListView(generics.ListAPIView):
    serializer_class = ERPProjectVisitSerializer

    def get_queryset(self):
        qs = ERPProjectVisit.objects.select_related(
            'project',
            'customer',
            'lead',
            'marketing_officer__user',
            'confirmed_by'
        ).all()

        project_id   = self.request.query_params.get('project')
        officer_id   = self.request.query_params.get('officer')
        visit_status = self.request.query_params.get('status')  # ✅ নাম বদলানো
        lead_id      = self.request.query_params.get('lead')

        if project_id:   qs = qs.filter(project_id=project_id)
        if officer_id:   qs = qs.filter(marketing_officer_id=officer_id)
        if visit_status: qs = qs.filter(status=visit_status)    # ✅
        if lead_id:      qs = qs.filter(lead_id=lead_id)

        return qs


class ERPProjectVisitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ERPProjectVisitSerializer

    def get_queryset(self):
        return ERPProjectVisit.objects.select_related(
            'project', 'customer', 'lead',
            'marketing_officer__user', 'confirmed_by'
        )

    def update(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_status  = request.data.get('status')
        save_kwargs = {}

        if new_status == 'confirmed' and not instance.confirmed_by_id:
            confirmed_by_id = request.data.get('confirmed_by')
            if not confirmed_by_id:
                return Response(
                    {'error': 'confirmed_by is required when confirming a visit.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            save_kwargs['confirmed_by_id'] = confirmed_by_id
            save_kwargs['confirmed_at']    = timezone.now()     # ✅ datetime.now() → timezone.now()

        visit = serializer.save(**save_kwargs)

        if new_status == 'completed' and visit.lead:
            visit.lead.status         = 'visited'
            visit.lead.last_contacted = timezone.now()          # ✅
            visit.lead.save()

        return Response(
            self.get_serializer(visit).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        visit = self.get_object()
        if visit.status == 'completed':
            return Response(
                {'error': 'Completed visit cannot be deleted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ERPProjectVisitCreateView(generics.CreateAPIView):
    serializer_class = ERPProjectVisitSerializer 

# =====================================================
# 12. MARKETING OFFICER VIEWS
# =====================================================

class ERPMarketingOfficerListView(generics.ListAPIView):
    serializer_class = ERPMarketingOfficerSerializer
    filter_backends  = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields    = [
        'user__full_name',
        'user__phone',
        'user__email',
        'officer_code',
        'rank',
    ]
    ordering_fields  = ['created_at', 'rank']
    ordering         = ['-created_at']

    def get_queryset(self):
        qs = ERPMarketingOfficer.objects.select_related('user').all()  # ✅ সব আসবে

        # ✅ Filter optional করা
        is_active = self.request.query_params.get('is_active')
        rank      = self.request.query_params.get('rank')

        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        if rank:
            qs = qs.filter(rank=rank)

        return qs

    def list(self, request, *args, **kwargs):
        queryset   = self.filter_queryset(self.get_queryset())
        page       = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
            })

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            'success': True,
            'count':   queryset.count(),
            'data':    serializer.data,
        })

class ERPMarketingOfficerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ERPMarketingOfficer.objects.all()
    serializer_class = ERPMarketingOfficerSerializer


class ERPMarketingOfficerCreateView(generics.CreateAPIView):
    queryset           = ERPMarketingOfficer.objects.all()
    serializer_class   = ERPMarketingOfficerSerializer
    permission_classes = [HasModulePermission]
    permission_module  = 'marketing'

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user')

        if not user_id:
            return Response({
                'success': False,
                'message': 'user_id দেওয়া আবশ্যক।',
            }, status=status.HTTP_400_BAD_REQUEST)

        if ERPMarketingOfficer.objects.filter(user_id=user_id).exists():
            return Response({
                'success': False,
                'message': 'এই user ইতিমধ্যে Marketing Officer হিসেবে আছে।',
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            officer = serializer.save()

            # ✅ Fresh data নিয়ে response দাও
            fresh = ERPMarketingOfficer.objects.select_related('user').get(pk=officer.pk)
            response_data = ERPMarketingOfficerSerializer(
                fresh, context={'request': request}
            ).data

            return Response({
                'success': True,
                'message': 'Marketing Officer তৈরি হয়েছে এবং role update হয়েছে।',
                'data': response_data,
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


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
    project_id = request.query_params.get('project')
    officer_id = request.query_params.get('officer')
    date_from  = request.query_params.get('date_from')
    date_to    = request.query_params.get('date_to')

    qs = Commission.objects.all()  # ← ERPCommission → Commission

    GENERATION_LABELS = {
    0: 'Direct',
    1: '1st', 2: '2nd', 3: '3rd',
    4: '4th', 5: '5th', 6: '6th', 7: '7th',
    }

    # officer filter থাকলে level 0 এর label এ officer এর নাম দেখাও
    if officer_id:
        try:
            officer = ERPUser.objects.get(id=officer_id)
            GENERATION_LABELS[0] = f'Direct ({officer.full_name})'
        except ERPUser.DoesNotExist:
            pass
    

    if project_id:
        qs = qs.filter(project_id=project_id)  # ← booking__project_id → project_id
    if officer_id:
        qs = qs.filter(user_id=officer_id)     # ← marketing_officer_id → user_id
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    SOURCE_TYPES = [
        'booking', 'installment', 'down_payment', 'investment',
        'registration', 'land_dev', 'parking', 'transfer', 'utility',
    ]


    # Overall Summary
    summary_agg = qs.aggregate(
        total_commission = Sum('commission'),       # ← commission_amount → commission
        total_paid       = Sum('commission', filter=Q(paid_at__isnull=False)),  # ← status='paid' → paid_at
        total_pending    = Sum('commission', filter=Q(paid_at__isnull=True)),
        total_officers   = Count('user', distinct=True),  # ← marketing_officer → user
    )

    # Generation-wise breakdown
    by_generation = []
    column_totals = {src: Decimal('0.00') for src in SOURCE_TYPES}
    grand_total   = Decimal('0.00')

    for gen in range(0, 8):
        row = {
        'level': gen,              
        'generation_label': GENERATION_LABELS.get(gen, f'Level {gen}'),
        }
        row_total = Decimal('0.00')

        for source in SOURCE_TYPES:
            agg = qs.filter(
                level=gen,                   
                commission_type=source      
            ).aggregate(
                total_amount = Sum('commission'),   # ← commission_amount → commission
                total_rate   = Sum('percent'),      # ← commission_rate → percent
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
    from mainapp.models import ERPWallet

    try:
        officer = ERPUser.objects.get(id=officer_id)
    except ERPUser.DoesNotExist:
        return Response({'error': 'Officer not found'}, status=404)

    commissions = Commission.objects.filter(user=officer).select_related(
        'project',
        'plot',
    )

    # ── Generation summary ────────────────────────────────────────────────
    gen_summary = {}
    for comm in commissions:
        gen = comm.level
        if gen not in gen_summary:
            gen_summary[gen] = {
                'level':          gen,
                'label':          'Direct' if gen == 0 else f'{gen}th',
                'count':          0,
                'total_amount':   Decimal('0.00'),
                'paid_amount':    Decimal('0.00'),
                'pending_amount': Decimal('0.00'),
            }
        gen_summary[gen]['count']        += 1
        gen_summary[gen]['total_amount'] += comm.commission
        if comm.paid_at:
            gen_summary[gen]['paid_amount']    += comm.commission
        else:
            gen_summary[gen]['pending_amount'] += comm.commission

    gen_list = [
        {
            **data,
            'total_amount':   float(data['total_amount']),
            'paid_amount':    float(data['paid_amount']),
            'pending_amount': float(data['pending_amount']),
        }
        for _, data in sorted(gen_summary.items())
    ]

    # ── Overall aggregate ─────────────────────────────────────────────────
    overall = commissions.aggregate(
        total=Sum('commission'),
        paid=Sum('commission', filter=Q(paid_at__isnull=False)),
    )

    # ── Wallet balance ────────────────────────────────────────────────────
    wallet_balance = 0
    try:
        wallet = ERPWallet.objects.get(user=officer)
        wallet_balance = float(wallet.balance)
    except Exception:
        pass

    # ── Project & Property ────────────────────────────────────────────────
    project_map  = {}
    property_map = {}

    for comm in commissions:
        if comm.project_id and comm.project_id not in project_map:
            project_map[comm.project_id] = {
                'id':   comm.project.id,
                'name': comm.project.project_name,
            }

        if comm.plot_id and comm.plot_id not in property_map:
            prop = comm.plot
            property_map[comm.plot_id] = {
                'id':         prop.id,
                'name':       prop.plot_number,
                'project_id': comm.project_id,
            }

    return Response({
        'officer': {
            'id':             officer.id,
            'username':       officer.username,
            'name':           officer.full_name,
            'roles':          officer.roles or [],
            'wallet_balance': wallet_balance,
        },
        'commission_summary': {
            'total':   float(overall['total'] or 0),
            'paid':    float(overall['paid']   or 0),
            'pending': float((overall['total'] or 0) - (overall['paid'] or 0)),
        },
        'by_level': gen_list,
        'projects':   list(project_map.values()),
        'properties': list(property_map.values()),
    })



# =====================================================
# 15. LOAN VIEWS
# =====================================================
from decimal import Decimal
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response

from decimal import Decimal
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response


class ERPLoanListView(generics.ListAPIView):
    serializer_class = ERPLoanSerializer

    def get_queryset(self):
        qs = ERPLoan.objects.select_related('employee__user', 'approved_by').all()  # ✅ employee__user

        employee_id = self.request.query_params.get('employee')
        loan_status = self.request.query_params.get('status')

        if employee_id: qs = qs.filter(employee_id=employee_id)
        if loan_status: qs = qs.filter(status=loan_status)

        return qs


class ERPLoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ERPLoanSerializer

    def get_queryset(self):
        return ERPLoan.objects.select_related('employee__user', 'approved_by')

    def destroy(self, request, *args, **kwargs):
        loan = self.get_object()
        if loan.status == 'paid':
            return Response(
                {'error': 'Paid loan cannot be deleted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ERPLoanCreateView(generics.CreateAPIView):
    serializer_class = ERPLoanSerializer

    def get_queryset(self):                                                          # ✅ যোগ করা হয়েছে
        return ERPLoan.objects.select_related('employee__user', 'approved_by')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                loan = serializer.save()

                # ✅ employee None কিনা আগে check করো
                if not loan.employee:
                    raise ValueError('Employee is required to create a loan.')

                wallet = ERPWallet.objects.filter(user=loan.employee.user).first()
                if wallet:
                    wallet.loan_balance += loan.loan_amount
                    wallet.save()
                else:
                    raise ValueError('Wallet not found for this employee.')

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            self.get_serializer(loan).data,
            status=status.HTTP_201_CREATED
        )



class ERPLoanRepaymentView(generics.UpdateAPIView):
    serializer_class  = ERPLoanSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return ERPLoan.objects.select_related('employee__user', 'approved_by')

    def patch(self, request, *args, **kwargs):
        loan = self.get_object()

        if loan.status == 'paid':
            return Response(
                {'error': 'This loan is already fully paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        repay_amount = request.data.get('repay_amount')
        if not repay_amount:
            return Response(
                {'error': 'repay_amount is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            repay_amount = Decimal(str(repay_amount))
        except Exception:
            return Response(
                {'error': 'repay_amount must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if repay_amount <= 0:
            return Response(
                {'error': 'repay_amount must be greater than 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if repay_amount > loan.remaining_amount:
            return Response(
                {'error': f'repay_amount cannot exceed remaining amount ({loan.remaining_amount}).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            loan.remaining_amount -= repay_amount
            loan.save()

            wallet = ERPWallet.objects.filter(user=loan.employee.user).first()
            if wallet:
                wallet.loan_balance -= repay_amount
                wallet.save()

        return Response(
            self.get_serializer(loan).data,
            status=status.HTTP_200_OK
        )


# =====================================================
# 16. INVESTOR VIEWS
# =====================================================

from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone as tz
from django.db import transaction


class ERPInvestorListView(generics.ListAPIView):
    serializer_class   = ERPInvestorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs        = ERPInvestor.objects.select_related('user').all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs


class ERPInvestorCreateView(generics.CreateAPIView):
    queryset           = ERPInvestor.objects.all()
    serializer_class   = ERPInvestorSerializer
    permission_classes = [IsAuthenticated]



class ERPInvestorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = ERPInvestor.objects.select_related('user').all()
    serializer_class   = ERPInvestorSerializer
    permission_classes = [IsAuthenticated]




class ERPInvestmentListView(generics.ListAPIView):
    serializer_class   = ERPInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs          = ERPInvestment.objects.select_related('investor__user', 'project').all()
        investor_id = self.request.query_params.get('investor')
        inv_status  = self.request.query_params.get('status')
        if investor_id:
            qs = qs.filter(investor_id=investor_id)
        if inv_status:
            qs = qs.filter(status=inv_status)
        return qs


class ERPInvestmentCreateView(generics.CreateAPIView):
    queryset           = ERPInvestment.objects.all()
    serializer_class   = ERPInvestmentSerializer
    permission_classes = [IsAuthenticated]


class ERPInvestmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = ERPInvestment.objects.select_related('investor__user', 'project').all()
    serializer_class   = ERPInvestmentSerializer
    permission_classes = [IsAuthenticated]


# ─────────────────────────────────────────────
# Dividend
# ─────────────────────────────────────────────

class ERPDividendListView(generics.ListAPIView):
    serializer_class   = ERPDividendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs            = ERPDividend.objects.select_related('investor__user', 'investment').all()
        investor_id   = self.request.query_params.get('investor')
        investment_id = self.request.query_params.get('investment')
        month         = self.request.query_params.get('month')
        year          = self.request.query_params.get('year')
        if investor_id:
            qs = qs.filter(investor_id=investor_id)
        if investment_id:
            qs = qs.filter(investment_id=investment_id)
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)
        return qs


class ERPDividendDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = ERPDividend.objects.all()
    serializer_class   = ERPDividendSerializer
    permission_classes = [IsAuthenticated]


class ERPDividendCreateView(generics.CreateAPIView):
    queryset           = ERPDividend.objects.all()
    serializer_class   = ERPDividendSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        investment_id = request.data.get('investment')
        month         = request.data.get('month')
        year          = request.data.get('year')

        if not all([investment_id, month, year]):
            return Response(
                {'error': 'investment, month এবং year আবশ্যক।'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            investment = ERPInvestment.objects.select_related(
                'investor__user'
            ).get(id=investment_id)

            # ── Active কিনা চেক ──
            if investment.status != 'active':
                return Response(
                    {'error': f'Investment টি active নয়, status: {investment.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ── Duplicate চেক ──
            if ERPDividend.objects.filter(
                investment=investment,
                month=month,
                year=year
            ).exists():
                return Response(
                    {'error': f'{month}/{year} মাসের dividend ইতিমধ্যে দেওয়া হয়েছে।'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ── Calculate ──
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
                    investment         = investment,
                    investor           = investment.investor,
                    month              = month,
                    year               = year,
                    base_amount        = base_amount,
                    dividend_rate      = rate_percent,
                    dividend_amount    = dividend_amount,
                    status             = 'paid',
                    wallet_credited    = True,
                    wallet_credited_at = tz.now(),
                )

                wallet.balance += dividend_amount
                wallet.save()

                investment.total_profit_received += dividend_amount
                investment.save(update_fields=['total_profit_received', 'updated_at'])

            return Response(
                self.get_serializer(dividend).data,
                status=status.HTTP_201_CREATED
            )

        except ERPInvestment.DoesNotExist:
            return Response({'error': 'Investment পাওয়া যায়নি।'}, status=404)
        except ERPWallet.DoesNotExist:
            return Response({'error': 'Investor wallet পাওয়া যায়নি।'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ─────────────────────────────────────────────
# Land Power
# ─────────────────────────────────────────────
class LandPowerViewSet(viewsets.ModelViewSet):
    queryset           = LandPowerAssignment.objects.select_related('investment').all()
    serializer_class   = LandPowerAssignmentSerializer
    permission_classes = [IsAuthenticated]



# =====================================================
# 17. HR VIEWS
# =====================================================
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from mainapp.models import ERPEmployee
from .serializers import ERPEmployeeSerializer


class ERPEmployeeListView(generics.ListAPIView):
    queryset           = ERPEmployee.objects.select_related('user').filter(user__is_active=True)
    serializer_class   = ERPEmployeeSerializer
    # permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]


class ERPEmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = ERPEmployee.objects.select_related('user').all()
    serializer_class   = ERPEmployeeSerializer
    # permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]


class ERPEmployeeCreateView(generics.CreateAPIView):
    queryset           = ERPEmployee.objects.all()
    serializer_class   = ERPEmployeeSerializer
    # permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]


from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from datetime import time, date

from mainapp.models import ERPAttendance, ERPAttendanceSummary, ERPEmployee
from mainapp.serializers import (
    ERPAttendanceSerializer,
    ERPAttendanceSummarySerializer,
    ERPCheckInSerializer,
    ERPCheckOutSerializer,
)
from mainapp.tasks import generate_monthly_summary

OFFICE_START_TIME = time(9, 0, 0)   # সকাল ৯টা


# ─────────────────────────────────────────────────────
# ১. Check-In View
# ─────────────────────────────────────────────────────


class ERPCheckInView(APIView):
    """
    POST /attendance/check-in/
    { "employee_id": 1, "device_log_id": "DEV-001" }

    - আজকে already check-in থাকলে error
    - ৯টার পরে আসলে → late
    - সব ঠিক থাকলে → present
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ERPCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_id   = serializer.validated_data['employee_id']
        device_log_id = serializer.validated_data.get('device_log_id', '')
        remarks       = serializer.validated_data.get('remarks', '')

        today    = timezone.localdate()
        now      = timezone.localtime()
        employee = ERPEmployee.objects.get(pk=employee_id)

        # ── Already check-in আছে কিনা চেক ──
        existing = ERPAttendance.objects.filter(
            employee        = employee,
            attendance_date = today
        ).first()

        if existing:
            if existing.check_in:
                return Response(
                    {'detail': f'আজকে ইতিমধ্যে check-in হয়েছে {existing.check_in.strftime("%H:%M")} তে।'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ── Late নির্ধারণ ──
        attendance_status = 'present'
        if now.time() > OFFICE_START_TIME:
            attendance_status = 'late'

        # ── Create বা Update ──
        attendance, created = ERPAttendance.objects.update_or_create(
            employee        = employee,
            attendance_date = today,
            defaults={
                'check_in'      : now,
                'status'        : attendance_status,
                'device_log_id' : device_log_id,
                'remarks'       : remarks,
                'marked_by'     : 'Device' if device_log_id else str(request.user),
            }
        )

        return Response({
            'detail'    : 'Check-in সফল।',
            'employee'  : employee.full_name,
            'check_in'  : attendance.check_in.strftime('%H:%M'),
            'status'    : attendance.status,
            'date'      : str(today),
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────
# ২. Check-Out View
# ─────────────────────────────────────────────────────

from decimal import Decimal


class ERPCheckOutView(APIView):
    """
    POST /attendance/check-out/
    { "employee_id": 1 }

    - Check-in না থাকলে error
    - Already check-out থাকলে error
    - total_hours auto calculate
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ERPCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_id   = serializer.validated_data['employee_id']
        device_log_id = serializer.validated_data.get('device_log_id', '')
        remarks       = serializer.validated_data.get('remarks', '')

        today      = timezone.localdate()
        now        = timezone.localtime()

        try:
            attendance = ERPAttendance.objects.get(
                employee_id     = employee_id,
                attendance_date = today
            )
        except ERPAttendance.DoesNotExist:
            return Response(
                {'detail': 'আজকের check-in পাওয়া যায়নি।'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Already check-out আছে কিনা ──
        if attendance.check_out:
            return Response(
                {'detail': f'আজকে ইতিমধ্যে check-out হয়েছে {attendance.check_out.strftime("%H:%M")} তে।'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── total_hours calculate ──
        total_hours = 0
        if attendance.check_in:
            delta       = now - attendance.check_in
            total_hours = round(delta.total_seconds() / 3600, 2)

        # ── half_day নির্ধারণ (৪ ঘণ্টার কম) ──
        if 0 < total_hours < 4 and attendance.status not in ('leave', 'holiday'):
            attendance.status = 'half_day'

        attendance.check_out     = now
        attendance.total_hours   = Decimal(str(total_hours))
        attendance.device_log_id = device_log_id or attendance.device_log_id
        attendance.remarks       = remarks or attendance.remarks
        attendance.save(update_fields=['check_out', 'total_hours', 'status', 'device_log_id', 'remarks'])

        return Response({
            'detail'      : 'Check-out সফল।',
            'employee'    : attendance.employee.full_name,
            'check_in'    : attendance.check_in.strftime('%H:%M'),
            'check_out'   : attendance.check_out.strftime('%H:%M'),
            'total_hours' : float(attendance.total_hours),
            'status'      : attendance.status,
            'date'        : str(today),
        }, status=status.HTTP_200_OK)
# ─────────────────────────────────────────────────────
# ৩. List / Detail / Create
# ─────────────────────────────────────────────────────
class ERPAttendanceListView(generics.ListAPIView):
    """GET /attendance/?employee=<id>&month=<m>&year=<y>&status=<s>"""
    serializer_class   = ERPAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs          = ERPAttendance.objects.select_related('employee__user').all()
        employee_id = self.request.query_params.get('employee')
        month       = self.request.query_params.get('month')
        year        = self.request.query_params.get('year')
        status      = self.request.query_params.get('status')

        if employee_id: qs = qs.filter(employee_id=employee_id)
        if month and year:
            qs = qs.filter(
                attendance_date__month=month,
                attendance_date__year=year
            )
        if status: qs = qs.filter(status=status)
        return qs


class ERPAttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = ERPAttendance.objects.select_related('employee__user').all()
    serializer_class   = ERPAttendanceSerializer
    permission_classes = [IsAuthenticated]


class ERPAttendanceCreateView(generics.CreateAPIView):
    """Manual attendance entry (HR এর জন্য)"""
    queryset           = ERPAttendance.objects.all()
    serializer_class   = ERPAttendanceSerializer
    permission_classes = [IsAuthenticated]


# ─────────────────────────────────────────────────────
# ৪. Summary Views
# ─────────────────────────────────────────────────────

class ERPAttendanceSummaryListView(generics.ListAPIView):
    serializer_class   = ERPAttendanceSummarySerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs          = ERPAttendanceSummary.objects.select_related('employee__user').all()
        employee_id = self.request.query_params.get('employee_id')
        month       = self.request.query_params.get('month')   # 2024-01

        if employee_id: qs = qs.filter(employee_id=employee_id)
        if month:
            year, m = month.split('-')
            qs = qs.filter(month__year=year, month__month=m)
        return qs



from .tasks import generate_monthly_summary # task ইমপোর্ট করে নিন

class GenerateMonthlySummaryView(APIView):
    """POST /attendance/summary/generate/ { "month": "2024-01" }"""
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        month = request.data.get('month')
        if month:
            year, m = month.split('-')
            # .delay() বাদ দিয়ে সরাসরি কল করুন
            generate_monthly_summary(int(year), int(m)) 
        else:
            generate_monthly_summary()
            
        return Response({'message': 'Summary generated successfully.'})



from mainapp.models import ERPHoliday
from mainapp.serializers import ERPHolidaySerializer

class ERPHolidayListCreateView(generics.ListCreateAPIView):
    queryset           = ERPHoliday.objects.all()
    serializer_class   = ERPHolidaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs    = super().get_queryset()
        year  = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if year:  qs = qs.filter(date__year=year)
        if month: qs = qs.filter(date__month=month)
        return qs

class ERPHolidayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = ERPHoliday.objects.all()
    serializer_class   = ERPHolidaySerializer
    permission_classes = [IsAuthenticated]




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
from django.utils import timezone


class ERPSMSLogListView(generics.ListAPIView):
    serializer_class = ERPSMSLogSerializer

    def get_queryset(self):
        qs = ERPSMSLog.objects.select_related(
            'customer__user',    # ✅ customer.user.full_name এর জন্য
            'booking',
            'officer__user'
        ).all()

        customer_id = self.request.query_params.get('customer')
        sms_type    = self.request.query_params.get('type')
        status      = self.request.query_params.get('status')
        booking_id  = self.request.query_params.get('booking')

        if customer_id: qs = qs.filter(customer_id=customer_id)
        if sms_type:    qs = qs.filter(sms_type=sms_type)
        if status:      qs = qs.filter(status=status)
        if booking_id:  qs = qs.filter(booking_id=booking_id)
        return qs


class ERPSMSLogDetailView(generics.RetrieveAPIView):
    serializer_class = ERPSMSLogSerializer

    def get_queryset(self):
        return ERPSMSLog.objects.select_related(
            'customer__user',    # ✅
            'booking',
            'officer__user'
        )


class ERPSMSLogCreateView(generics.CreateAPIView):
    serializer_class = ERPSMSLogSerializer

    # ✅ CreateAPIView এ get_queryset দরকার নেই, সরিয়ে দেওয়া হয়েছে

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.status == 'sent' and not instance.sent_at:
            instance.sent_at = timezone.now()  # ✅ datetime.now() → timezone.now()
            instance.save()

# =====================================================
# 22. DOCUMENT VIEWS
# =====================================================


class ERPDocumentListView(generics.ListAPIView):
    serializer_class = ERPDocumentSerializer

    def get_queryset(self):
        # ✅ bug fix + select_related
        qs = ERPDocument.objects.select_related(
            'booking', 'project', 'customer', 'created_by'
        ).all()

        booking_id  = self.request.query_params.get('booking')
        doc_type    = self.request.query_params.get('type')
        customer_id = self.request.query_params.get('customer')
        project_id  = self.request.query_params.get('project')

        if booking_id:
            qs = qs.filter(booking_id=booking_id)
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if project_id:
            qs = qs.filter(project_id=project_id)

        return qs


class ERPDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ERPDocumentSerializer

    def get_queryset(self):
        return ERPDocument.objects.select_related(
            'booking', 'project', 'customer', 'created_by'
        )


class ERPDocumentCreateView(generics.CreateAPIView):
    serializer_class = ERPDocumentSerializer

    def get_queryset(self):
        return ERPDocument.objects.select_related(
            'booking', 'project', 'customer', 'created_by'
        )

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
    serializer_class = ERPSystemLogSerializer

    def get_queryset(self):
        # ✅ select_related
        qs = ERPSystemLog.objects.select_related('user').all()

        log_level = self.request.query_params.get('level')
        module    = self.request.query_params.get('module')
        user_id   = self.request.query_params.get('user')

        if log_level:
            qs = qs.filter(log_level=log_level)
        if module:
            qs = qs.filter(module=module)
        if user_id:
            qs = qs.filter(user_id=user_id)

        return qs


# ✅ Detail view যোগ করা হয়েছে — শুধু GET
class ERPSystemLogDetailView(generics.RetrieveAPIView):
    serializer_class = ERPSystemLogSerializer

    def get_queryset(self):
        return ERPSystemLog.objects.select_related('user')


class ERPSystemLogCreateView(generics.CreateAPIView):
    serializer_class = ERPSystemLogSerializer

    def get_queryset(self):
        return ERPSystemLog.objects.select_related('user')

    # ✅ IP address auto-capture
    def perform_create(self, serializer):
        ip = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        serializer.save(ip_address=ip)


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

    total_plots     = Property.objects.count()
    available_plots = Property.objects.filter(status='available').count()
    booked_plots    = Property.objects.filter(status='booked').count()
    sold_plots      = Property.objects.filter(status='sold').count()

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


#======================================================
# 25.             LAND MANAGEMENT
#======================================================




# ── Supplier ──────────────────────────────────────────────
class ERPSupplierListView(generics.ListAPIView):
    queryset         = ERPSupplier.objects.filter(is_active=True)
    serializer_class = ERPSupplierSerializer
    filter_backends  = [SearchFilter, OrderingFilter]
    search_fields    = ['supplier_code', 'full_name', 'phone', 'email']
    ordering_fields  = ['created_at', 'full_name']

class ERPSupplierCreateView(generics.CreateAPIView):
    queryset         = ERPSupplier.objects.all()
    serializer_class = ERPSupplierSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]

class ERPSupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = ERPSupplier.objects.all()
    serializer_class = ERPSupplierSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]


# ── Land Owner ───────────────────────────────────────────
class ERPLandOwnerListView(generics.ListAPIView):
    queryset         = ERPLandOwner.objects.all()
    serializer_class = ERPLandOwnerSerializer
    filter_backends  = [SearchFilter]
    search_fields    = ['full_name', 'nid']

class ERPLandOwnerCreateView(generics.CreateAPIView):
    queryset         = ERPLandOwner.objects.all()
    serializer_class = ERPLandOwnerSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]

class ERPLandOwnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = ERPLandOwner.objects.all()
    serializer_class = ERPLandOwnerSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]


# ── Land Acquisition ─────────────────────────────────────
class ERPLandAcquisitionListView(generics.ListAPIView):
    queryset         = ERPLandAcquisition.objects.select_related('supplier', 'land_owner')
    serializer_class = ERPLandAcquisitionSerializer
    filter_backends  = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class  = ERPLandAcquisitionFilter
    search_fields    = [
        'acquisition_code', 'khatiyan_number',
        'supplier__full_name', 'land_owner__full_name',
    ]
    ordering_fields  = ['created_at', 'total_value', 'area_purchased']

class ERPLandAcquisitionCreateView(generics.CreateAPIView):
    queryset         = ERPLandAcquisition.objects.all()
    serializer_class = ERPLandAcquisitionSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]

class ERPLandAcquisitionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = ERPLandAcquisition.objects.select_related('supplier', 'land_owner')
    serializer_class = ERPLandAcquisitionSerializer
    parser_classes   = [MultiPartParser, FormParser, JSONParser]




#================================================================
#                   COMMISSION TYPE VIEWS
#==============================================================



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Percentage
from .serializers import PercentageSerializer


class PercentageViewSet(viewsets.ModelViewSet):
    queryset = Percentage.objects.all()
    serializer_class = PercentageSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        transaction_type = request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Percentage deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=['get'], url_path='by-type/(?P<transaction_type>[^/.]+)')
    def by_type(self, request, transaction_type=None):
        queryset = self.get_queryset().filter(transaction_type=transaction_type)
        if not queryset.exists():
            return Response(
                {"detail": f"No records found for type '{transaction_type}'."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    


