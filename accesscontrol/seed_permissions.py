# management/commands/seed_permissions.py
# =====================================================
# Default permission গুলো database এ insert করা
# python manage.py seed_permissions
# =====================================================

from django.core.management.base import BaseCommand
from mainapp.models import ERPPermission, ERPRolePermission


# সব module এর সব action
ALL_PERMISSIONS = [
    # module,           action,   description
    ('project',         'view',   'Project list ও detail দেখা'),
    ('plot',            'view',   'Plot list ও detail দেখা'),
    ('booking',         'view',   'Booking দেখা'),
    ('booking',         'create', 'নতুন Booking তৈরি করা'),
    ('booking',         'edit',   'Booking edit করা'),
    ('installment',     'view',   'Installment plan দেখা'),
    ('receipt',         'view',   'Money receipt দেখা'),
    ('receipt',         'create', 'নতুন receipt তৈরি করা'),
    ('commission',      'view',   'Commission দেখা'),
    ('wallet',          'view',   'Wallet দেখা'),
    ('lead',            'view',   'Lead দেখা'),
    ('lead',            'create', 'নতুন lead তৈরি করা'),
    ('lead',            'edit',   'Lead edit করা'),
    ('attendance',      'view',   'Attendance দেখা'),
    ('payroll',         'view',   'Payroll দেখা'),
    ('investment',      'view',   'Investment দেখা'),
    ('dividend',        'view',   'Dividend দেখা'),
    ('officer_request', 'view',   'Officer request দেখা'),
    ('officer_request', 'create', 'নতুন request তৈরি করা'),
    ('document',        'view',   'Document দেখা'),
    ('offer',           'view',   'Offer দেখা'),
]

# Role → Permission → Scope mapping
DEFAULT_ROLE_PERMISSIONS = [

    # ── Employee ──────────────────────────────────────
    ('employee', 'project.view',     'all'),
    ('employee', 'plot.view',        'all'),
    ('employee', 'attendance.view',  'own'),
    ('employee', 'payroll.view',     'own'),
    ('employee', 'wallet.view',      'own'),
    ('employee', 'offer.view',       'all'),

    # ── Marketing Officer ─────────────────────────────
    ('marketing_officer', 'project.view',          'all'),
    ('marketing_officer', 'plot.view',             'all'),
    ('marketing_officer', 'booking.view',          'own'),
    ('marketing_officer', 'installment.view',      'own'),
    ('marketing_officer', 'receipt.view',          'own'),
    ('marketing_officer', 'commission.view',       'own'),
    ('marketing_officer', 'wallet.view',           'own'),
    ('marketing_officer', 'lead.view',             'own'),
    ('marketing_officer', 'lead.create',           'own'),
    ('marketing_officer', 'lead.edit',             'own'),
    ('marketing_officer', 'officer_request.view',  'own'),
    ('marketing_officer', 'officer_request.create','own'),
    ('marketing_officer', 'document.view',         'own'),
    ('marketing_officer', 'offer.view',            'all'),

    # ── Marketing Manager (Officer এর সব + extra) ────
    ('marketing_manager', 'project.view',          'all'),
    ('marketing_manager', 'plot.view',             'all'),
    ('marketing_manager', 'booking.view',          'own'),
    ('marketing_manager', 'installment.view',      'own'),
    ('marketing_manager', 'receipt.view',          'own'),
    ('marketing_manager', 'commission.view',       'own'),
    ('marketing_manager', 'wallet.view',           'own'),
    ('marketing_manager', 'lead.view',             'own'),
    ('marketing_manager', 'lead.create',           'own'),
    ('marketing_manager', 'lead.edit',             'own'),
    ('marketing_manager', 'officer_request.view',  'own'),
    ('marketing_manager', 'officer_request.create','own'),
    ('marketing_manager', 'document.view',         'own'),
    ('marketing_manager', 'offer.view',            'all'),

    # ── Customer ─────────────────────────────────────
    ('customer', 'project.view',     'all'),
    ('customer', 'plot.view',        'all'),
    ('customer', 'booking.view',     'own'),
    ('customer', 'installment.view', 'own'),
    ('customer', 'receipt.view',     'own'),
    ('customer', 'wallet.view',      'own'),
    ('customer', 'document.view',    'own'),
    ('customer', 'offer.view',       'all'),

    # ── Investor ─────────────────────────────────────
    ('investor', 'project.view',    'all'),
    ('investor', 'plot.view',       'all'),
    ('investor', 'investment.view', 'own'),
    ('investor', 'dividend.view',   'own'),
    ('investor', 'wallet.view',     'own'),
    ('investor', 'document.view',   'own'),
    ('investor', 'offer.view',      'all'),
]


class Command(BaseCommand):
    help = 'Default permission গুলো database এ insert করে'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔐 Permission seeding শুরু হচ্ছে...\n')

        # Step 1: ERPPermission তৈরি করা
        created_perms = 0
        for module, action, description in ALL_PERMISSIONS:
            _, created = ERPPermission.objects.get_or_create(
                module=module,
                action=action,
                defaults={'description': description}
            )
            if created:
                created_perms += 1

        self.stdout.write(f'  ✅ {created_perms} নতুন permission তৈরি হয়েছে\n')

        # Step 2: ERPRolePermission তৈরি করা
        created_role_perms = 0
        errors = []

        for role, codename, scope in DEFAULT_ROLE_PERMISSIONS:
            try:
                perm = ERPPermission.objects.get(codename=codename)
                _, created = ERPRolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                    defaults={'scope': scope, 'is_active': True}
                )
                if created:
                    created_role_perms += 1
            except ERPPermission.DoesNotExist:
                errors.append(f'Permission not found: {codename}')

        self.stdout.write(f'  ✅ {created_role_perms} নতুন role permission তৈরি হয়েছে\n')

        if errors:
            for err in errors:
                self.stdout.write(f'  ⚠️  {err}\n')

        self.stdout.write('\n✅ Permission seeding সম্পন্ন!\n')
        self.stdout.write('এখন চালান: python manage.py runserver\n')
