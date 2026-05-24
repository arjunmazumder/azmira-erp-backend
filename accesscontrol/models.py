from django.db import models

# =====================================================
# models.py এ add করুন — Dynamic Permission System
# =====================================================


class ERPPermission(models.Model):
    """
    System এর সব possible permission গুলো define করে।
    যেমন: booking.view, booking.create, installment.view
    """

    MODULE_CHOICES = [
        ('project',       'Project'),
        ('property',      'Property'),
        ('booking',       'Booking'),
        ('installment',   'Installment'),
        ('receipt',       'Money Receipt'),
        ('commission',    'Commission'),
        ('wallet',        'Wallet'),
        ('lead',          'Lead'),
        ('attendance',    'Attendance'),
        ('payroll',       'Payroll'),
        ('investment',    'Investment'),
        ('dividend',      'Dividend'),
        ('officer_request', 'Officer Request'),
        ('document',      'Document'),
        ('offer',         'Offer'),
    ]

    ACTION_CHOICES = [
        ('view',   'View'),
        ('create', 'Create'),
        ('edit',   'Edit'),
        ('delete', 'Delete'),
    ]

    id          = models.BigAutoField(primary_key=True)
    codename    = models.CharField(max_length=100, unique=True)  # e.g. 'booking.view'
    module      = models.CharField(max_length=50, choices=MODULE_CHOICES)
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=200, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['module', 'action']
        unique_together = [['module', 'action']]

    def __str__(self):
        return self.codename

    def save(self, *args, **kwargs):
        # codename auto-generate: module.action
        self.codename = f'{self.module}.{self.action}'
        super().save(*args, **kwargs)


class ERPRolePermission(models.Model):
    """
    কোন role কোন permission পাবে সেটা define করে।
    Admin এখান থেকে যেকোনো সময় change করতে পারবে।
    """

    ROLE_CHOICES = [
        ('employee',          'Employee'),
        ('marketing_officer', 'Marketing Officer'),
        ('marketing_manager', 'Marketing Manager'),
        ('customer',          'Customer'),
        ('investor',          'Investor'),
    ]

    SCOPE_CHOICES = [
        ('own',  'Own Data Only'),   # শুধু নিজের data
        ('all',  'All Data'),        # সব data
    ]

    id         = models.BigAutoField(primary_key=True)
    role       = models.CharField(max_length=50, choices=ROLE_CHOICES)
    permission = models.ForeignKey(
        ERPPermission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    scope = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default='own',
        help_text="own = শুধু নিজের data, all = সব data"
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['role', 'permission__module']
        unique_together = [['role', 'permission']]

    def __str__(self):
        return f'{self.role} → {self.permission.codename} ({self.scope})'
