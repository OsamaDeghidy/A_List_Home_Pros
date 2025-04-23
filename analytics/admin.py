from django.contrib import admin
from .models import DashboardStat, ContractorStat, ServiceCategoryStat, UserActivity, SearchQuery


@admin.register(DashboardStat)
class DashboardStatAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'new_users', 'new_contractors', 'new_appointments', 'completed_appointments', 'total_payment_volume']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContractorStat)
class ContractorStatAdmin(admin.ModelAdmin):
    list_display = ['id', 'contractor', 'date', 'profile_views', 'appointment_requests', 'completed_appointments', 'total_earnings', 'average_rating']
    list_filter = ['date', 'contractor']
    search_fields = ['contractor__business_name', 'contractor__user__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ServiceCategoryStat)
class ServiceCategoryStatAdmin(admin.ModelAdmin):
    list_display = ['id', 'service_category', 'date', 'contractor_count', 'appointment_count', 'average_price']
    list_filter = ['date', 'service_category']
    search_fields = ['service_category__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'activity_type', 'description_preview', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'user__name', 'description', 'ip_address']
    readonly_fields = ['created_at', 'updated_at']
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'query_preview', 'results_count', 'created_at']
    list_filter = ['created_at', 'results_count']
    search_fields = ['user__email', 'user__name', 'query']
    readonly_fields = ['created_at', 'updated_at']
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'
