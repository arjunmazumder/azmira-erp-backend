from rest_framework.permissions import BasePermission
from accesscontrol.models import ERPRolePermission


# --- হেল্পার ফাংশন (রোলস লিস্টকে ক্লিন করার জন্য) ---
def get_clean_roles(user):
    """ইউজারের রোলস ফিল্ড স্ট্রিং বা লিস্ট যা-ই হোক, তা ছোট হাতের অক্ষরে ক্লিন লিস্ট বানায়"""
    if not user or not getattr(user, 'roles', None):
        return []
    if isinstance(user.roles, list):
        return [str(r).strip().lower() for r in user.roles if r]
    return [r.strip().lower() for r in str(user.roles).split(',') if r.strip()]


# --- ১. নির্দিষ্ট একক রোলের পারমিশন ক্লাসসমূহ ---

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        roles = get_clean_roles(request.user)
        return request.user and request.user.is_authenticated and 'customer' in roles

class IsInvestor(BasePermission):
    def has_permission(self, request, view):
        roles = get_clean_roles(request.user)
        return request.user and request.user.is_authenticated and 'investor' in roles

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        roles = get_clean_roles(request.user)
        return request.user and request.user.is_authenticated and 'employee' in roles

class IsMarketingOfficer(BasePermission):
    def has_permission(self, request, view):
        roles = get_clean_roles(request.user)
        return request.user and request.user.is_authenticated and 'marketing_officer' in roles

class IsMarketingManager(BasePermission):
    def has_permission(self, request, view):
        roles = get_clean_roles(request.user)
        return request.user and request.user.is_authenticated and 'marketing_manager' in roles

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        roles = get_clean_roles(request.user)
        return 'admin' in roles or 'super_admin' in roles

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        roles = get_clean_roles(request.user)
        return request.user and request.user.is_authenticated and 'super_admin' in roles


# --- ২. গ্লোবাল ডায়নামিক মডিউল ভিত্তিক পারমিশন ক্লাস ---

class HasModulePermission(BasePermission):
    """
    View এ permission_module define করলে automatically
    method অনুযায়ী DB থেকে permission check করবে।
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # HTTP Method → Action Mapping
        method_action_map = {
            'GET':    'view',
            'POST':   'create',
            'PUT':    'edit',
            'PATCH':  'edit',
            'DELETE': 'delete',
        }
        action = method_action_map.get(request.method)
        if not action:
            return False

        # View এ permission_module ডিক্লেয়ার করা থাকতে হবে (যেমন: permission_module = 'booking')
        module = getattr(view, 'permission_module', None)
        if not module:
            return False

        # রোলসগুলো ক্লিন করে নিয়ে আসা
        user_roles = get_clean_roles(request.user)

        # Admin বা SuperAdmin হলে সরাসরি ফুল এক্সেস (কোনো ডাটাবেজ কুয়েরি লাগবে না)
        if 'admin' in user_roles or 'super_admin' in user_roles:
            return True

        if not user_roles:
            return False

        # ডাটাবেজ থেকে পারমিশন চেক করা
        # নোট: ডাটাবেজে যদি রোলের নাম ক্যাপিটাল লেটারে থাকে (যেমন: "Manager") 
        # তবে role__in=user_roles এর জায়গায় কুয়েরি করার সুবিধার্থে মডেলে যেভাবে সেভ করা আছে সেভাবে মেলানো উচিত।
        # ডাটাবেজে যেভাবে কেস (Case) আছে তা হ্যান্ডেল করতে নিচে __in কুয়েরি করা হলো:
        return ERPRolePermission.objects.filter(
            role__in=user_roles,  
            permission__module=module.lower().strip(),
            permission__action=action.lower().strip(),
            is_active=True
        ).exists()


# --- ৩. accesscontrol.py এর জন্য হেল্পার ফাংশন ---
def get_role_permissions(role):
    """
    একটি নির্দিষ্ট রোলের জন্য ডাটাবেজ থেকে সমস্ত পারমিশন ডিকশনারি আকারে নিয়ে আসে।
    এটি আপনার accesscontrol.py ফাইলে কল করা হয়।
    """
    if not role:
        return {}
        
    # ডাটাবেজ থেকে এই রোলের একটিভ পারমিশনগুলো তুলে আনা
    permissions = ERPRolePermission.objects.filter(
        role__iexact=str(role).strip(), # কেস ইনসেনসিটিভ কুয়েরি (Manager/manager দুইটাই কাজ করবে)
        is_active=True
    ).select_related('permission')
    
    perms_dict = {}
    for p in permissions:
        if p.permission:
            # কোডনেম ফরম্যাট: 'module.action' (যেমন: 'booking.view')
            codename = f"{p.permission.module}.{p.permission.action}"
            # স্কোপ ডিফল্ট হিসেবে 'all' বা 'own' যা মডেলে আছে (মডেলে না থাকলে ডিফল্ট 'own')
            scope = getattr(p, 'scope', 'own') or 'own'
            perms_dict[codename] = scope
            
    return perms_dict