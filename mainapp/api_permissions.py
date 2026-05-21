from rest_framework.permissions import BasePermission

# Apnar permissions.py file-e jodi ei class-ti na thake, tobe eta add korun:
class IsAdminOrSuperAdmin(BasePermission):
    """Admin othoba Super Admin dynamic permission rule"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        user_roles = request.user.roles or []
        return 'admin' in user_roles or 'super_admin' in user_roles

class IsSuperAdmin(BasePermission):
    """Shudu Super Admin access pabe"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and 'super_admin' in (request.user.roles or [])

class IsAdmin(BasePermission):
    """Super Admin ebong Regular Admin access pabe"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        user_roles = request.user.roles or []
        print(user_roles)
        return 'admin' in user_roles or 'super_admin' in user_roles

class IsMarketingUser(BasePermission):
    """Marketing Manager ba Officer access pabe (Apnar property use kore)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_marketing

class IsAccountsOfficer(BasePermission):
    """Shudu Accounts Officer access pabe"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and 'accounts' in (request.user.roles or [])