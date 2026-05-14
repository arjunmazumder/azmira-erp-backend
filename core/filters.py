import django_filters
from mainapp.models import ERPPlot
from mainapp.models import ERPProject
from mainapp.models import ERPLandAcquisition


class ERPPlotFilter(django_filters.FilterSet):
    
    # 💰 Price range
    min_price = django_filters.NumberFilter(field_name="final_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="final_price", lookup_expr='lte')

    # 📏 Area range
    min_area = django_filters.NumberFilter(field_name="area", lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name="area", lookup_expr='lte')

    class Meta:
        model = ERPPlot
        fields = [
            'project',
            'status',
            'plot_type',
            'facing',
            'bedrooms',
            'bathrooms',
            'floor_number',
        ]


class ERPProjectFilter(django_filters.FilterSet):

    # 💰 Project value range
    min_value = django_filters.NumberFilter(
        field_name="total_project_value",
        lookup_expr='gte'
    )
    max_value = django_filters.NumberFilter(
        field_name="total_project_value",
        lookup_expr='lte'
    )

    # 📏 Land area range
    min_area = django_filters.NumberFilter(
        field_name="total_land_area",
        lookup_expr='gte'
    )
    max_area = django_filters.NumberFilter(
        field_name="total_land_area",
        lookup_expr='lte'
    )

    # 📅 Date filters
    launch_date_after = django_filters.DateFilter(
        field_name="launch_date",
        lookup_expr='gte'
    )
    launch_date_before = django_filters.DateFilter(
        field_name="launch_date",
        lookup_expr='lte'
    )

    completion_date_after = django_filters.DateFilter(
        field_name="completion_date",
        lookup_expr='gte'
    )
    completion_date_before = django_filters.DateFilter(
        field_name="completion_date",
        lookup_expr='lte'
    )

    class Meta:
        model = ERPProject
        fields = [
            'project_name',
            'project_type',
            'status',
            'city',
            'district',
            'upazila',
        ]





class ERPLandAcquisitionFilter(django_filters.FilterSet):

    # Supplier & owner
    supplier    = django_filters.NumberFilter(field_name='supplier__id')
    land_owner  = django_filters.NumberFilter(field_name='land_owner__id')

    # Status dropdowns
    land_status = django_filters.ChoiceFilter(
        choices=ERPLandAcquisition.LAND_STATUS_CHOICES
    )
    is_mutated  = django_filters.BooleanFilter()
    is_surveyed = django_filters.BooleanFilter()

    # Price range
    min_price   = django_filters.NumberFilter(field_name='price_per_decimal', lookup_expr='gte')
    max_price   = django_filters.NumberFilter(field_name='price_per_decimal', lookup_expr='lte')

    # Area range
    min_area    = django_filters.NumberFilter(field_name='total_area', lookup_expr='gte')
    max_area    = django_filters.NumberFilter(field_name='total_area', lookup_expr='lte')

    # Total value range
    min_value   = django_filters.NumberFilter(field_name='total_value', lookup_expr='gte')
    max_value   = django_filters.NumberFilter(field_name='total_value', lookup_expr='lte')

    # Date range
    date_from   = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    date_to     = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')

    class Meta:
        model  = ERPLandAcquisition
        fields = [
            'supplier', 'land_owner', 'land_status',
            'is_mutated', 'is_surveyed',
        ]