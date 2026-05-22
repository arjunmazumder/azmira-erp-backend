from django.contrib import admin
from .models import ERPPermission, ERPRolePermission

@admin.register(ERPPermission)
class ERPPermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'module', 'action', 'description']
    list_filter  = ['module', 'action']

@admin.register(ERPRolePermission)
class ERPRolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'scope', 'is_active']
    list_filter  = ['role', 'scope', 'is_active']