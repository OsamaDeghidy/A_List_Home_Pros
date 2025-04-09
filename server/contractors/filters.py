import django_filters
from django.db.models import Q, Avg
from .models import ContractorProfile, ServiceCategory


class ContractorFilter(django_filters.FilterSet):
    """Advanced filter for contractors"""
    service_category = django_filters.ModelMultipleChoiceFilter(
        field_name='service_categories',
        queryset=ServiceCategory.objects.all(),
        label='Service Category'
    )
    
    location = django_filters.CharFilter(
        method='filter_location',
        label='Location'
    )
    
    min_rating = django_filters.NumberFilter(
        method='filter_min_rating',
        label='Minimum Rating'
    )
    
    years_in_business = django_filters.NumberFilter(
        field_name='years_in_business',
        lookup_expr='gte',
        label='Minimum Years in Business'
    )
    
    availability = django_filters.BooleanFilter(
        method='filter_availability',
        label='Has Availability'
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = ContractorProfile
        fields = ['service_category', 'location', 'min_rating', 'years_in_business', 'availability', 'search']
    
    def filter_location(self, queryset, name, value):
        """Filter by location (city, state, zip)"""
        if not value:
            return queryset
        
        # Split the location string to handle city, state, or zip
        terms = value.split(',')
        q_objects = Q()
        
        for term in terms:
            term = term.strip()
            if not term:
                continue
                
            # Check if term is a zip code (all digits)
            if term.isdigit():
                q_objects |= Q(user__addresses__zip_code__icontains=term)
            else:
                q_objects |= Q(user__addresses__city__icontains=term) | Q(user__addresses__state__icontains=term)
        
        return queryset.filter(q_objects).distinct()
    
    def filter_min_rating(self, queryset, name, value):
        """Filter by minimum average rating"""
        if not value:
            return queryset
            
        # Annotate queryset with average rating and filter
        return queryset.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__gte=value)
    
    def filter_availability(self, queryset, name, value):
        """Filter by whether contractor has availability slots set up"""
        if value is None:
            return queryset
            
        if value:
            # Has at least one availability slot
            return queryset.filter(availability_slots__isnull=False).distinct()
        else:
            # Has no availability slots
            return queryset.filter(availability_slots__isnull=True)
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value:
            return queryset
            
        # Split search terms
        terms = value.split()
        q_objects = Q()
        
        for term in terms:
            q_objects |= (
                Q(business_name__icontains=term) |
                Q(description__icontains=term) |
                Q(user__name__icontains=term) |
                Q(service_categories__name__icontains=term)
            )
        
        return queryset.filter(q_objects).distinct()
