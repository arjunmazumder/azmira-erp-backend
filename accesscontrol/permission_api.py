# =====================================================
# serializers.py এ add করুন
# =====================================================
from rest_framework import serializers
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mainapp.models import ERPPermission, ERPRolePermission

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
            'id', 'role', 'role_display', 'permission', 'permission_codename',
            'permission_module', 'permission_action',
            'scope', 'scope_display', 'is_active',
            'updated_by', 'created_at', 'updated_at',
        ]

    def get_scope_display(self, obj): return obj.get_scope_display()
    def get_role_display(self, obj):  return obj.get_role_display()


# =====================================================
# views.py এ add করুন
# =====================================================

from mainapp.models      import ERPPermission, ERPRolePermission
from mainapp.serializers import ERPPermissionSerializer, ERPRolePermissionSerializer
from accesscontrol.permissions     import clear_permission_cache


class ERPPermissionListView(generics.ListAPIView):
    """GET /api/permissions/ — সব permission এর list"""
    queryset         = ERPPermission.objects.all()
    serializer_class = ERPPermissionSerializer
    filter_backends  = [SearchFilter]
    search_fields    = ['codename', 'module', 'action']


class ERPRolePermissionListView(generics.ListAPIView):
    """
    GET /api/role-permissions/
    ?role=employee / ?role=marketing_officer / ?role=customer / ?role=investor
    """
    serializer_class = ERPRolePermissionSerializer

    def get_queryset(self):
        qs   = ERPRolePermission.objects.select_related('permission').all()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs


class ERPRolePermissionUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/role-permissions/<id>/
    Admin একটি permission এর scope বা is_active change করতে পারবে।

    Request body:
    {
        "scope": "all",        ← 'own' বা 'all'
        "is_active": false     ← permission বন্ধ করা
    }
    """
    queryset         = ERPRolePermission.objects.all()
    serializer_class = ERPRolePermissionSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        instance   = self.get_object()
        old_role   = instance.role

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=str(request.user))

        # Cache clear — পুরনো permission cache মুছে দেওয়া
        clear_permission_cache(old_role)

        return Response({
            'message':    f'"{instance.role}" এর "{instance.permission.codename}" permission update হয়েছে।',
            'permission': serializer.data,
        })


class ERPRolePermissionCreateView(generics.CreateAPIView):
    """
    POST /api/role-permissions/create/
    Admin নতুন permission assign করতে পারবে।

    Request body:
    {
        "role":       "marketing_officer",
        "permission": 3,
        "scope":      "own"
    }
    """
    queryset         = ERPRolePermission.objects.all()
    serializer_class = ERPRolePermissionSerializer

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=str(self.request.user))
        clear_permission_cache(instance.role)


class ERPRolePermissionDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/role-permissions/<id>/delete/
    Admin একটি permission সম্পূর্ণ remove করতে পারবে।
    """
    queryset         = ERPRolePermission.objects.all()
    serializer_class = ERPRolePermissionSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        role     = instance.role
        codename = instance.permission.codename
        instance.delete()
        clear_permission_cache(role)
        return Response({
            'message': f'"{role}" থেকে "{codename}" permission remove হয়েছে।'
        })


@api_view(['GET'])
def role_permission_summary(request):
    """
    GET /api/role-permission-summary/
    Admin dashboard এর জন্য — সব role এর permission একসাথে।

    Response:
    {
        "employee": [
            {"codename": "project.view", "scope": "all", "is_active": true},
            ...
        ],
        "customer": [...],
        ...
    }
    """
    roles = ['employee', 'marketing_officer', 'marketing_manager', 'customer', 'investor']
    result = {}

    for role in roles:
        perms = ERPRolePermission.objects.filter(
            role=role
        ).select_related('permission').order_by('permission__module', 'permission__action')

        result[role] = [
            {
                'id':       rp.id,
                'codename': rp.permission.codename,
                'module':   rp.permission.module,
                'action':   rp.permission.action,
                'scope':    rp.scope,
                'is_active':rp.is_active,
            }
            for rp in perms
        ]

    return Response(result)


# =====================================================
# urls.py এ add করুন
# =====================================================

"""
from api.views import (
    ERPPermissionListView,
    ERPRolePermissionListView,
    ERPRolePermissionUpdateView,
    ERPRolePermissionCreateView,
    ERPRolePermissionDeleteView,
    role_permission_summary,
)

urlpatterns += [
    path('permissions/',                      ERPPermissionListView.as_view(),       name='permission-list'),
    path('role-permissions/',                 ERPRolePermissionListView.as_view(),   name='role-permission-list'),
    path('role-permissions/create/',          ERPRolePermissionCreateView.as_view(), name='role-permission-create'),
    path('role-permissions/<int:pk>/',        ERPRolePermissionUpdateView.as_view(), name='role-permission-update'),
    path('role-permissions/<int:pk>/delete/', ERPRolePermissionDeleteView.as_view(), name='role-permission-delete'),
    path('role-permission-summary/',          role_permission_summary,               name='role-permission-summary'),
]
"""
