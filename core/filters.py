import django_filters
from mainapp.models import ERPPlot
from mainapp.models import ERPProject


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
            'project_type',
            'status',
            'city',
            'district',
            'upazila',
        ]