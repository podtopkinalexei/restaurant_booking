import django_filters

from .models import Reservation, Table


class ReservationFilter(django_filters.FilterSet):
    """Фильтр для бронирований"""
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    time_from = django_filters.TimeFilter(field_name='time', lookup_expr='gte')
    time_to = django_filters.TimeFilter(field_name='time', lookup_expr='lte')
    min_guests = django_filters.NumberFilter(field_name='guests', lookup_expr='gte')
    max_guests = django_filters.NumberFilter(field_name='guests', lookup_expr='lte')

    class Meta:
        model = Reservation
        fields = {
            'status': ['exact', 'in'],
            'table__table_type': ['exact'],
            'table__number': ['exact', 'icontains'],
        }


class TableFilter(django_filters.FilterSet):
    """Фильтр для столиков"""
    min_capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    available_only = django_filters.BooleanFilter(field_name='is_available')

    class Meta:
        model = Table
        fields = ['table_type', 'is_available']
