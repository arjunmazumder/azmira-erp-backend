# api/permissions.py
# =====================================================
# Dynamic Permission System — Database থেকে পড়ে
# =====================================================

from django.core.cache import cache
from rest_framework.permissions import BasePermission


# =====================================================
# CACHE HELPER
# =====================================================

CACHE_TTL = 60 * 5  # 5 minutes


def get_role_permissions(role):
    """
    একটি role এর সব active permission cache থেকে আনা।
    Return: { 'booking.view': 'own', 'project.view': 'all', ... }
    """
    cache_key = f'erp_permissions_{role}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from mainapp.models import ERPRolePermission
    role_perms = ERPRolePermission.objects.filter(
        role=role,
        is_active=True
    ).select_related('permission')

    result = {
        rp.permission.codename: rp.scope
        for rp in role_perms
    }

    cache.set(cache_key, result, CACHE_TTL)
    return result


def clear_permission_cache(role=None):
    """Admin permission change করলে cache clear করা।"""
    if role:
        cache.delete(f'erp_permissions_{role}')
    else:
        for r in ['employee', 'marketing_officer', 'marketing_manager', 'customer', 'investor']:
            cache.delete(f'erp_permissions_{r}')


# =====================================================
# HELPERS
# =====================================================

def get_erp_user(request):
    user = request.user
    if not user or not hasattr(user, 'erp_user'):
        return None
    return user.erp_user


def get_user_roles(request):
    erp_user = get_erp_user(request)
    if not erp_user:
        return []
    return list(erp_user.roles or [])


def user_has_permission(request, codename):
    roles = get_user_roles(request)
    for role in roles:
        perms = get_role_permissions(role)
        if codename in perms:
            return True
    return False


def user_permission_scope(request, codename):
    """'all' > 'own' — যদি কোনো role এ 'all' থাকে সেটা return করে।"""
    roles = get_user_roles(request)
    scope = None
    for role in roles:
        perms = get_role_permissions(role)
        if codename in perms:
            if perms[codename] == 'all':
                return 'all'
            scope = perms[codename]
    return scope


# =====================================================
# BASE PERMISSION
# =====================================================

class ERPBasePermission(BasePermission):
    message = 'আপনার এই কাজের permission নেই।'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            self.message = 'Login করুন।'
            return False
        erp_user = get_erp_user(request)
        if not erp_user:
            self.message = 'ERP User profile পাওয়া যায়নি।'
            return False
        if not erp_user.is_active:
            self.message = 'আপনার account deactivated।'
            return False
        return True


# =====================================================
# PERMISSION FACTORY
# =====================================================

class HasERPPermissionFactory:
    """
    ব্যবহার:
        CanViewBooking = HasERPPermissionFactory('booking.view')
        permission_classes = [CanViewBooking]
    """
    def __new__(cls, codename):
        class _Permission(ERPBasePermission):
            _codename = codename
            message   = f'আপনার "{codename}" permission নেই।'

            def has_permission(self, request, view):
                if not super().has_permission(request, view):
                    return False
                has_perm = user_has_permission(request, self._codename)
                if not has_perm:
                    self.message = f'আপনার "{self._codename}" permission নেই।'
                return has_perm

        _Permission.__name__ = f'Can_{codename.replace(".", "_")}'
        return _Permission


# =====================================================
# PRE-BUILT PERMISSIONS — views.py এ সরাসরি use করুন
# =====================================================

CanViewProject         = HasERPPermissionFactory('project.view')
CanViewProperty        = HasERPPermissionFactory('property.view')
CanViewBooking         = HasERPPermissionFactory('booking.view')
CanCreateBooking       = HasERPPermissionFactory('booking.create')
CanEditBooking         = HasERPPermissionFactory('booking.edit')
CanViewInstallment     = HasERPPermissionFactory('installment.view')
CanViewReceipt         = HasERPPermissionFactory('receipt.view')
CanCreateReceipt       = HasERPPermissionFactory('receipt.create')
CanViewCommission      = HasERPPermissionFactory('commission.view')
CanViewWallet          = HasERPPermissionFactory('wallet.view')
CanViewLead            = HasERPPermissionFactory('lead.view')
CanCreateLead          = HasERPPermissionFactory('lead.create')
CanEditLead            = HasERPPermissionFactory('lead.edit')
CanViewAttendance      = HasERPPermissionFactory('attendance.view')
CanViewPayroll         = HasERPPermissionFactory('payroll.view')
CanViewInvestment      = HasERPPermissionFactory('investment.view')
CanViewDividend        = HasERPPermissionFactory('dividend.view')
CanViewOfficerRequest  = HasERPPermissionFactory('officer_request.view')
CanCreateOfficerRequest= HasERPPermissionFactory('officer_request.create')
CanViewDocument        = HasERPPermissionFactory('document.view')
CanViewOffer           = HasERPPermissionFactory('offer.view')


# =====================================================
# OBJECT LEVEL PERMISSION
# scope 'own' হলে নিজের data, 'all' হলে সব
# =====================================================

class ERPObjectPermission(ERPBasePermission):
    codename = None

    def has_object_permission(self, request, view, obj):
        erp_user = get_erp_user(request)
        if not erp_user:
            return False

        scope = user_permission_scope(request, self.codename)

        if scope == 'all':
            return True

        if scope == 'own':
            return self._is_owner(erp_user, obj)

        return False

    def _is_owner(self, erp_user, obj):
        # booking → customer → user
        if hasattr(obj, 'customer') and obj.customer:
            if hasattr(obj.customer, 'user') and obj.customer.user_id == erp_user.id:
                return True
        # booking → marketing_officer → user
        if hasattr(obj, 'marketing_officer') and obj.marketing_officer:
            if hasattr(obj.marketing_officer, 'user') and obj.marketing_officer.user_id == erp_user.id:
                return True
        # investment/dividend → investor → user
        if hasattr(obj, 'investor') and obj.investor:
            if hasattr(obj.investor, 'user') and obj.investor.user_id == erp_user.id:
                return True
        # attendance/payroll → employee → user
        if hasattr(obj, 'employee') and obj.employee:
            if hasattr(obj.employee, 'user') and obj.employee.user_id == erp_user.id:
                return True
        # direct user field
        if hasattr(obj, 'user') and obj.user_id == erp_user.id:
            return True
        return False


class BookingObjectPermission(ERPObjectPermission):
    codename = 'booking.view'

class InstallmentObjectPermission(ERPObjectPermission):
    codename = 'installment.view'

class ReceiptObjectPermission(ERPObjectPermission):
    codename = 'receipt.view'

class InvestmentObjectPermission(ERPObjectPermission):
    codename = 'investment.view'

class AttendanceObjectPermission(ERPObjectPermission):
    codename = 'attendance.view'