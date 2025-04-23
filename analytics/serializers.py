from rest_framework import serializers
from .models import DashboardStat, ContractorStat, ServiceCategoryStat, UserActivity, SearchQuery


class DashboardStatSerializer(serializers.ModelSerializer):
    """Serializer for dashboard statistics"""
    class Meta:
        model = DashboardStat
        fields = [
            'id', 'date', 'new_users', 'new_contractors', 'new_appointments',
            'completed_appointments', 'total_payment_volume', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContractorStatSerializer(serializers.ModelSerializer):
    """Serializer for contractor statistics"""
    class Meta:
        model = ContractorStat
        fields = [
            'id', 'contractor', 'date', 'profile_views', 'appointment_requests',
            'completed_appointments', 'cancelled_appointments', 'total_earnings',
            'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceCategoryStatSerializer(serializers.ModelSerializer):
    """Serializer for service category statistics"""
    class Meta:
        model = ServiceCategoryStat
        fields = [
            'id', 'service_category', 'date', 'contractor_count',
            'appointment_count', 'average_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity"""
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'description',
            'ip_address', 'user_agent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for search queries"""
    class Meta:
        model = SearchQuery
        fields = [
            'id', 'user', 'query', 'filters', 'results_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
