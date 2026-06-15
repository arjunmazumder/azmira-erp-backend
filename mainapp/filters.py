from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from mainapp.models import( Transaction,ERPUser)

class TransactionFilter(django_filters.FilterSet):
    # Exact matches
    transaction_type = django_filters.ChoiceFilter(choices=Transaction.TRANSACTION_TYPE)
    customer         = django_filters.NumberFilter(field_name='customer__id')
    project          = django_filters.NumberFilter(field_name='project__id')
    plot             = django_filters.NumberFilter(field_name='plot__id')
    referred_by      = django_filters.NumberFilter(field_name='referred_by__id')
    transferred_to   = django_filters.NumberFilter(field_name='transferred_to__id')

    # Amount range
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    # Date range
    created_after  = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after  = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    # Boolean-style helpers
    has_transfer_target = django_filters.BooleanFilter(
        field_name='transferred_to', lookup_expr='isnull', exclude=True
    )
    has_referral = django_filters.BooleanFilter(
        field_name='referred_by', lookup_expr='isnull', exclude=True
    )

    class Meta:
        model  = Transaction
        fields = [
            'transaction_type', 'customer', 'project', 'plot',
            'referred_by', 'transferred_to',
            'amount_min', 'amount_max',
            'created_after', 'created_before',
            'updated_after', 'updated_before',
            'has_transfer_target', 'has_referral',
        ]



class ERPUserFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name='is_active')
    role = django_filters.CharFilter(method='filter_by_role')

    def filter_by_role(self, queryset, name, value):
        # JSONField এ role filter — "marketing_officer" দিলে সেই role আছে এমন user দেখাবে
        return queryset.filter(roles__icontains=f'"{value}"')

    class Meta:
        model = ERPUser
        fields = ['is_active', 'role']
