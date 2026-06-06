# management/commands/seed_permissions.py
# python manage.py seed_permissions

from django.core.management.base import BaseCommand
from accesscontrol.models import ERPPermission, ERPRolePermission


ALL_PERMISSIONS = [
    # module,              action,   description
    # ── Project ──────────────────────────────────────
    ('project',         'view',   'Project list ও detail দেখা'),
    ('project',         'create', 'নতুন Project তৈরি করা'),
    ('project',         'edit',   'Project edit করা'),
    ('project',         'delete', 'Project delete করা'),

    # ── Property (Plot/Flat) ──────────────────────────
    ('property',        'view',   'Plot/Flat list ও detail দেখা'),
    ('property',        'create', 'নতুন Plot/Flat তৈরি করা'),
    ('property',        'edit',   'Plot/Flat edit করা'),
    ('property',        'delete', 'Plot/Flat delete করা'),

    # ── Customer ─────────────────────────────────────
    ('customer',        'view',   'Customer list ও detail দেখা'),
    ('customer',        'create', 'নতুন Customer তৈরি করা'),
    ('customer',        'edit',   'Customer edit করা'),
    ('customer',        'delete', 'Customer delete করা'),

    # ── Lead ─────────────────────────────────────────
    ('lead',            'view',   'Lead দেখা'),
    ('lead',            'create', 'নতুন Lead তৈরি করা'),
    ('lead',            'edit',   'Lead edit করা'),
    ('lead',            'delete', 'Lead delete করা'),

    # ── Booking ──────────────────────────────────────
    ('booking',         'view',   'Booking দেখা'),
    ('booking',         'create', 'নতুন Booking তৈরি করা'),
    ('booking',         'edit',   'Booking edit করা'),
    ('booking',         'delete', 'Booking delete করা'),

    # ── Installment ──────────────────────────────────
    ('installment',     'view',   'Installment plan দেখা'),
    ('installment',     'create', 'নতুন Installment তৈরি করা'),
    ('installment',     'edit',   'Installment edit করা'),
    ('installment',     'delete', 'Installment delete করা'),

    # ── Money Receipt ─────────────────────────────────
    ('receipt',         'view',   'Money receipt দেখা'),
    ('receipt',         'create', 'নতুন receipt তৈরি করা'),
    ('receipt',         'edit',   'Receipt edit করা'),
    ('receipt',         'delete', 'Receipt delete করা'),

    # ── Voucher ──────────────────────────────────────
    ('voucher',         'view',   'Voucher দেখা'),
    ('voucher',         'create', 'নতুন Voucher তৈরি করা'),
    ('voucher',         'edit',   'Voucher edit করা'),
    ('voucher',         'delete', 'Voucher delete করা'),

    # ── Commission ────────────────────────────────────
    ('commission',      'view',   'Commission দেখা'),
    ('commission',      'create', 'নতুন Commission তৈরি করা'),
    ('commission',      'edit',   'Commission edit করা'),
    ('commission',      'delete', 'Commission delete করা'),

    # ── Wallet ───────────────────────────────────────
    ('wallet',          'view',   'Wallet দেখা'),
    ('wallet',          'create', 'Wallet transaction তৈরি করা'),
    ('wallet',          'edit',   'Wallet edit করা'),
    ('wallet',          'delete', 'Wallet entry delete করা'),

    # ── Project Visit ─────────────────────────────────
    ('project_visit',   'view',   'Project visit দেখা'),
    ('project_visit',   'create', 'নতুন visit schedule করা'),
    ('project_visit',   'edit',   'Visit edit করা'),
    ('project_visit',   'delete', 'Visit delete করা'),

    # ── Marketing Officer ─────────────────────────────
    ('marketing_officer', 'view',   'Marketing officer দেখা'),
    ('marketing_officer', 'create', 'নতুন officer তৈরি করা'),
    ('marketing_officer', 'edit',   'Officer edit করা'),
    ('marketing_officer', 'delete', 'Officer delete করা'),

    # ── Officer Request (TA/DA) ───────────────────────
    ('officer_request', 'view',   'Officer request দেখা'),
    ('officer_request', 'create', 'নতুন request তৈরি করা'),
    ('officer_request', 'edit',   'Request edit করা'),
    ('officer_request', 'delete', 'Request delete করা'),

    # ── Land Record ──────────────────────────────────
    ('land_record',     'view',   'Land record দেখা'),
    ('land_record',     'create', 'নতুন land record তৈরি করা'),
    ('land_record',     'edit',   'Land record edit করা'),
    ('land_record',     'delete', 'Land record delete করা'),

    # ── Land Acquisition ─────────────────────────────
    ('land_acquisition', 'view',   'Land acquisition দেখা'),
    ('land_acquisition', 'create', 'নতুন acquisition তৈরি করা'),
    ('land_acquisition', 'edit',   'Acquisition edit করা'),
    ('land_acquisition', 'delete', 'Acquisition delete করা'),

    # ── Investor ─────────────────────────────────────
    ('investor',        'view',   'Investor দেখা'),
    ('investor',        'create', 'নতুন Investor তৈরি করা'),
    ('investor',        'edit',   'Investor edit করা'),
    ('investor',        'delete', 'Investor delete করা'),

    # ── Investment ────────────────────────────────────
    ('investment',      'view',   'Investment দেখা'),
    ('investment',      'create', 'নতুন Investment তৈরি করা'),
    ('investment',      'edit',   'Investment edit করা'),
    ('investment',      'delete', 'Investment delete করা'),

    # ── Dividend ─────────────────────────────────────
    ('dividend',        'view',   'Dividend দেখা'),
    ('dividend',        'create', 'নতুন Dividend তৈরি করা'),
    ('dividend',        'edit',   'Dividend edit করা'),
    ('dividend',        'delete', 'Dividend delete করা'),

    # ── Employee ─────────────────────────────────────
    ('employee',        'view',   'Employee দেখা'),
    ('employee',        'create', 'নতুন Employee তৈরি করা'),
    ('employee',        'edit',   'Employee edit করা'),
    ('employee',        'delete', 'Employee delete করা'),

    # ── Attendance ────────────────────────────────────
    ('attendance',      'view',   'Attendance দেখা'),
    ('attendance',      'create', 'Attendance তৈরি করা'),
    ('attendance',      'edit',   'Attendance edit করা'),
    ('attendance',      'delete', 'Attendance delete করা'),

    # ── Payroll ──────────────────────────────────────
    ('payroll',         'view',   'Payroll দেখা'),
    ('payroll',         'create', 'নতুন Payroll তৈরি করা'),
    ('payroll',         'edit',   'Payroll edit করা'),
    ('payroll',         'delete', 'Payroll delete করা'),

    # ── Loan ─────────────────────────────────────────
    ('loan',            'view',   'Loan দেখা'),
    ('loan',            'create', 'নতুন Loan তৈরি করা'),
    ('loan',            'edit',   'Loan edit করা'),
    ('loan',            'delete', 'Loan delete করা'),

    # ── Account Head ─────────────────────────────────
    ('account_head',    'view',   'Account head দেখা'),
    ('account_head',    'create', 'নতুন account head তৈরি করা'),
    ('account_head',    'edit',   'Account head edit করা'),
    ('account_head',    'delete', 'Account head delete করা'),

    # ── Offer ────────────────────────────────────────
    ('offer',           'view',   'Offer দেখা'),
    ('offer',           'create', 'নতুন Offer তৈরি করা'),
    ('offer',           'edit',   'Offer edit করা'),
    ('offer',           'delete', 'Offer delete করা'),

    # ── Plot ─────────────────────────────────────────
    ('plot',            'view',   'Plot দেখা'),
    ('plot',            'create', 'নতুন Plot তৈরি করা'),
    ('plot',            'edit',   'Plot edit করা'),
    ('plot',            'delete', 'Plot delete করা'),

    # ── Document ─────────────────────────────────────
    ('document',        'view',   'Document দেখা'),
    ('document',        'create', 'নতুন Document আপলোড করা'),
    ('document',        'edit',   'Document edit করা'),
    ('document',        'delete', 'Document delete করা'),

    # ── SMS Log ──────────────────────────────────────
    ('sms_log',         'view',   'SMS log দেখা'),
    ('sms_log',         'create', 'SMS পাঠানো'),
    ('sms_log',         'edit',   'SMS log edit করা'),
    ('sms_log',         'delete', 'SMS log delete করা'),

    # ── Company Asset ────────────────────────────────
    ('company_asset',   'view',   'Company asset দেখা'),
    ('company_asset',   'create', 'নতুন asset তৈরি করা'),
    ('company_asset',   'edit',   'Asset edit করা'),
    ('company_asset',   'delete', 'Asset delete করা'),

    # ── System Log ───────────────────────────────────
    ('system_log',      'view',   'System log দেখা'),
    ('system_log',      'create', 'Log তৈরি করা'),
    ('system_log',      'edit',   'Log edit করা'),
    ('system_log',      'delete', 'Log delete করা'),

    # ── Transaction ──────────────────────────────────
    ('transaction',     'view',   'Transaction দেখা'),
    ('transaction',     'create', 'নতুন transaction তৈরি করা'),
    ('transaction',     'edit',   'Transaction edit করা'),
    ('transaction',     'delete', 'Transaction delete করা'),
]


DEFAULT_ROLE_PERMISSIONS = [

    # ══════════════════════════════════════════════════
    # EMPLOYEE
    # ══════════════════════════════════════════════════
    ('employee', 'project.view',        'all'),
    ('employee', 'property.view',       'all'),
    ('employee', 'plot.view',           'all'),
    ('employee', 'offer.view',          'all'),
    ('employee', 'attendance.view',     'own'),
    ('employee', 'payroll.view',        'own'),
    ('employee', 'wallet.view',         'own'),
    ('employee', 'loan.view',           'own'),
    ('employee', 'document.view',       'own'),

    # ══════════════════════════════════════════════════
    # MARKETING OFFICER
    # ══════════════════════════════════════════════════
    ('marketing_officer', 'project.view',           'all'),
    ('marketing_officer', 'property.view',          'all'),
    ('marketing_officer', 'plot.view',              'all'),
    ('marketing_officer', 'customer.view',          'own'),
    ('marketing_officer', 'customer.create',        'own'),
    ('marketing_officer', 'lead.view',              'own'),
    ('marketing_officer', 'lead.create',            'own'),
    ('marketing_officer', 'lead.edit',              'own'),
    ('marketing_officer', 'booking.view',           'own'),
    ('marketing_officer', 'installment.view',       'own'),
    ('marketing_officer', 'receipt.view',           'own'),
    ('marketing_officer', 'commission.view',        'own'),
    ('marketing_officer', 'wallet.view',            'own'),
    ('marketing_officer', 'project_visit.view',     'own'),
    ('marketing_officer', 'project_visit.create',   'own'),
    ('marketing_officer', 'project_visit.edit',     'own'),
    ('marketing_officer', 'officer_request.view',   'own'),
    ('marketing_officer', 'officer_request.create', 'own'),
    ('marketing_officer', 'officer_request.edit',   'own'),
    ('marketing_officer', 'document.view',          'own'),
    ('marketing_officer', 'offer.view',             'all'),

    # ══════════════════════════════════════════════════
    # MARKETING MANAGER
    # ══════════════════════════════════════════════════
    ('marketing_manager', 'project.view',             'all'),
    ('marketing_manager', 'property.view',            'all'),
    ('marketing_manager', 'plot.view',                'all'),
    ('marketing_manager', 'customer.view',            'all'),
    ('marketing_manager', 'customer.create',          'all'),
    ('marketing_manager', 'customer.edit',            'all'),
    ('marketing_manager', 'lead.view',                'all'),
    ('marketing_manager', 'lead.create',              'all'),
    ('marketing_manager', 'lead.edit',                'all'),
    ('marketing_manager', 'lead.delete',              'all'),
    ('marketing_manager', 'booking.view',             'all'),
    ('marketing_manager', 'installment.view',         'all'),
    ('marketing_manager', 'receipt.view',             'all'),
    ('marketing_manager', 'commission.view',          'all'),
    ('marketing_manager', 'wallet.view',              'own'),
    ('marketing_manager', 'project_visit.view',       'all'),
    ('marketing_manager', 'project_visit.create',     'all'),
    ('marketing_manager', 'project_visit.edit',       'all'),
    ('marketing_manager', 'officer_request.view',     'all'),
    ('marketing_manager', 'officer_request.create',   'own'),
    ('marketing_manager', 'officer_request.edit',     'own'),
    ('marketing_manager', 'document.view',            'all'),
    ('marketing_manager', 'offer.view',               'all'),
    ('marketing_manager', 'marketing_officer.view',   'all'),

    # ══════════════════════════════════════════════════
    # CUSTOMER
    # ══════════════════════════════════════════════════
    ('customer', 'project.view',      'all'),
    ('customer', 'property.view',     'all'),
    ('customer', 'plot.view',         'all'),
    ('customer', 'booking.view',      'own'),
    ('customer', 'installment.view',  'own'),
    ('customer', 'receipt.view',      'own'),
    ('customer', 'transaction.view',  'own'),
    ('customer', 'wallet.view',       'own'),
    ('customer', 'document.view',     'own'),
    ('customer', 'offer.view',        'all'),

    # ══════════════════════════════════════════════════
    # INVESTOR
    # ══════════════════════════════════════════════════
    ('investor', 'project.view',     'all'),
    ('investor', 'property.view',    'all'),
    ('investor', 'plot.view',        'all'),
    ('investor', 'investment.view',  'own'),
    ('investor', 'dividend.view',    'own'),
    ('investor', 'wallet.view',      'own'),
    ('investor', 'document.view',    'own'),
    ('investor', 'offer.view',       'all'),
]


class Command(BaseCommand):
    help = 'সব model এর default permission গুলো database এ insert করে'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='আগের সব permission মুছে নতুন করে insert করবে',
        )

    def handle(self, *args, **kwargs):
        reset = kwargs.get('reset', False)

        if reset:
            ERPRolePermission.objects.all().delete()
            ERPPermission.objects.all().delete()
            self.stdout.write('🗑️  আগের সব permission মুছে ফেলা হয়েছে\n')

        self.stdout.write('🔐 Permission seeding শুরু হচ্ছে...\n')

        # ── Step 1: ERPPermission তৈরি ──────────────────
        created_perms = 0
        for module, action, description in ALL_PERMISSIONS:
            _, created = ERPPermission.objects.get_or_create(
                module=module,
                action=action,
                defaults={'description': description}
            )
            if created:
                created_perms += 1

        total_perms = ERPPermission.objects.count()
        self.stdout.write(f'  ✅ {created_perms} নতুন permission তৈরি (মোট: {total_perms})\n')

        # ── Step 2: ERPRolePermission তৈরি ──────────────
        created_role_perms = 0
        errors = []

        for role, codename, scope in DEFAULT_ROLE_PERMISSIONS:
            try:
                module, action = codename.split('.')          # ✅ fix
                perm = ERPPermission.objects.get(
                    module=module,
                    action=action
                )
                _, created = ERPRolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                    defaults={'scope': scope, 'is_active': True}
                )
                if created:
                    created_role_perms += 1
            except ERPPermission.DoesNotExist:
                errors.append(f'❌ Permission পাওয়া যায়নি: {codename}')
            except ValueError:
                errors.append(f'❌ Invalid codename format: {codename}')

        total_role_perms = ERPRolePermission.objects.count()
        self.stdout.write(f'  ✅ {created_role_perms} নতুন role permission তৈরি (মোট: {total_role_perms})\n')

        # ── Errors ──────────────────────────────────────
        if errors:
            self.stdout.write('\n⚠️  কিছু সমস্যা হয়েছে:\n')
            for err in errors:
                self.stdout.write(f'  {err}\n')

        # ── Summary ─────────────────────────────────────
        self.stdout.write('\n📊 Summary:\n')
        for role in ['employee', 'marketing_officer', 'marketing_manager', 'customer', 'investor']:
            count = ERPRolePermission.objects.filter(role=role, is_active=True).count()
            self.stdout.write(f'  {role:<25} → {count} permissions\n')

        self.stdout.write('\n✅ Permission seeding সম্পন্ন!\n')