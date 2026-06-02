from django.db import models
from mainapp.models import ERPUser


# =====================================================
# Module level এ define করুন — সব model ব্যবহার করতে পারবে
# =====================================================

SCOPE_CHOICES = [
    ('own',  'Own Data Only'),
    ('team', 'Team Data'),
    ('all',  'All Data'),
]

ROLE_CHOICES = [
    ('super_admin',       'Super Admin'),
    ('admin',             'Admin'),
    ('accounts',          'Accounts Officer'),
    ('hr',                'HR Manager'),
    ('customer_care',     'Customer Care'),
    ('employee',          'Employee'),
    ('marketing_officer', 'Marketing Officer'),
    ('marketing_manager', 'Marketing Manager'),
    ('customer',          'Customer'),
    ('investor',          'Investor'),
]


# =====================================================
# ERPPermission
# =====================================================

class ERPPermission(models.Model):

    MODULE_CHOICES = [
        ('user',            'User Management'),
        ('project',         'Project'),
        ('property',        'Property'),
        ('booking',         'Booking'),
        ('installment',     'Installment'),
        ('receipt',         'Money Receipt'),
        ('commission',      'Commission'),
        ('wallet',          'Wallet'),
        ('lead',            'Lead'),
        ('attendance',      'Attendance'),
        ('payroll',         'Payroll'),
        ('investment',      'Investment'),
        ('dividend',        'Dividend'),
        ('officer_request', 'Officer Request'),
        ('document',        'Document'),
        ('offer',           'Offer'),
        ('project_visit',   'Project Visit'),
        ('land_record',     'Land Record'),
        ('customer',        'Customer'),
        ('employee',        'Employee'),
        ('loan',            'Loan'),
        ('voucher',         'Voucher'),
        ('asset',           'Company Asset'),
        ('sms',             'SMS Log'),
        ('report',          'Report'),
    ]

    ACTION_CHOICES = [
        ('view',     'View'),
        ('create',   'Create'),
        ('edit',     'Edit'),
        ('delete',   'Delete'),
        ('approve',  'Approve'),
        ('cancel',   'Cancel'),
        ('transfer', 'Transfer'),
        ('export',   'Export'),
        ('download', 'Download'),
    ]

    id          = models.BigAutoField(primary_key=True)
    codename    = models.CharField(max_length=100, unique=True)
    module      = models.CharField(max_length=50, choices=MODULE_CHOICES)
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=200, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering      = ['module', 'action']
        unique_together = [['module', 'action']]

    def __str__(self):
        return self.codename

    def save(self, *args, **kwargs):
        self.codename = f'{self.module}.{self.action}'
        super().save(*args, **kwargs)


# =====================================================
# ERPRolePermission
# =====================================================

class ERPRolePermission(models.Model):

    id         = models.BigAutoField(primary_key=True)
    role       = models.CharField(max_length=50, choices=ROLE_CHOICES)
    permission = models.ForeignKey(
        ERPPermission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    scope      = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='own')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering        = ['role', 'permission__module']
        unique_together = [['role', 'permission']]

    def __str__(self):
        return f'{self.role} → {self.permission.codename} ({self.scope})'


