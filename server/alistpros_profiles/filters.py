import django_filters
from .models import AListHomeProProfile


class AListHomeProFilter(django_filters.FilterSet):
    """
    Filter for A-List Home Pro profiles
    """
    business_name = django_filters.CharFilter(lookup_expr='icontains')
    min_years_experience = django_filters.NumberFilter(field_name='years_of_experience', lookup_expr='gte')
    service_category = django_filters.NumberFilter(field_name='service_categories', lookup_expr='exact')
    service_radius = django_filters.NumberFilter(field_name='service_radius', lookup_expr='gte')
    is_onboarded = django_filters.BooleanFilter()
    
    class Meta:
        model = AListHomeProProfile
        fields = [
            'business_name', 
            'min_years_experience', 
            'service_category',
            'service_radius',
            'is_onboarded'
        ]
