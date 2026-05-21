


from django.urls import path
from accesscontrol.views import force_seed_permissions  

urlpatterns = [
    path('force-seed/', force_seed_permissions),
    
]

# from permission_api import (
#     ERPPermissionListView,
#     ERPRolePermissionListView,
#     ERPRolePermissionUpdateView,
#     ERPRolePermissionCreateView,
#     ERPRolePermissionDeleteView,
#     role_permission_summary,
# )
# urlpatterns += [
#     path('permissions/',                      ERPPermissionListView.as_view(),       name='permission-list'),
#     path('role-permissions/',                 ERPRolePermissionListView.as_view(),   name='role-permission-list'),
#     path('role-permissions/create/',          ERPRolePermissionCreateView.as_view(), name='role-permission-create'),
#     path('role-permissions/<int:pk>/',        ERPRolePermissionUpdateView.as_view(), name='role-permission-update'),
#     path('role-permissions/<int:pk>/delete/', ERPRolePermissionDeleteView.as_view(), name='role-permission-delete'),
#     path('role-permission-summary/',          role_permission_summary,               name='role-permission-summary'),
# ]