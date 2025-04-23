from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import DashboardStat, ContractorStat, ServiceCategoryStat, UserActivity, SearchQuery
from .serializers import (
    DashboardStatSerializer,
    ContractorStatSerializer,
    ServiceCategoryStatSerializer,
    UserActivitySerializer,
    SearchQuerySerializer
)
from users.permissions import IsAdmin
from contractors.models import ContractorProfile, ServiceCategory
from scheduling.models import Appointment
from payments.models import Payment

User = get_user_model()


class AnalyticsDashboardViewSet(viewsets.ViewSet):
    """ViewSet for analytics dashboard data"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def platform_overview(self, request):
        """Get platform-wide statistics"""
        # Only admins can see platform-wide stats
        if not request.user.is_admin:
            return Response(
                {'detail': 'You do not have permission to view platform statistics.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Get latest dashboard stats
        try:
            latest_stats = DashboardStat.objects.latest()
            stats_serializer = DashboardStatSerializer(latest_stats)
            dashboard_stats = stats_serializer.data
        except DashboardStat.DoesNotExist:
            dashboard_stats = {
                'date': today,
                'new_users': 0,
                'new_contractors': 0,
                'new_appointments': 0,
                'completed_appointments': 0,
                'total_payment_volume': 0
            }
        
        # Get current counts
        user_count = User.objects.count()
        contractor_count = ContractorProfile.objects.count()
        appointment_count = Appointment.objects.count()
        
        # Get 30-day stats
        new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        new_contractors_30d = ContractorProfile.objects.filter(created_at__gte=thirty_days_ago).count()
        new_appointments_30d = Appointment.objects.filter(created_at__gte=thirty_days_ago).count()
        completed_appointments_30d = Appointment.objects.filter(
            status='COMPLETED',
            updated_at__gte=thirty_days_ago
        ).count()
        
        # Get payment volume
        payment_volume = Payment.objects.filter(
            status='COMPLETED',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))
        
        # Get top service categories
        top_categories = ServiceCategory.objects.annotate(
            contractor_count=Count('contractors')
        ).order_by('-contractor_count')[:5]
        
        top_categories_data = [
            {
                'id': category.id,
                'name': category.name,
                'contractor_count': category.contractor_count
            }
            for category in top_categories
        ]
        
        # Get top contractors by rating
        top_contractors = ContractorProfile.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-avg_rating')[:5]
        
        top_contractors_data = [
            {
                'id': contractor.id,
                'business_name': contractor.business_name,
                'avg_rating': contractor.avg_rating,
                'review_count': contractor.review_count
            }
            for contractor in top_contractors
        ]
        
        return Response({
            'dashboard_stats': dashboard_stats,
            'current_counts': {
                'user_count': user_count,
                'contractor_count': contractor_count,
                'appointment_count': appointment_count,
            },
            'thirty_day_stats': {
                'new_users': new_users_30d,
                'new_contractors': new_contractors_30d,
                'new_appointments': new_appointments_30d,
                'completed_appointments': completed_appointments_30d,
                'payment_volume': payment_volume.get('total', 0) if payment_volume.get('total') else 0
            },
            'top_categories': top_categories_data,
            'top_contractors': top_contractors_data
        })
    
    @action(detail=False, methods=['get'])
    def contractor_dashboard(self, request):
        """Get contractor-specific dashboard data"""
        # Check if user is a contractor
        if not hasattr(request.user, 'contractor_profile'):
            return Response(
                {'detail': 'You do not have a contractor profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        contractor = request.user.contractor_profile
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Get contractor stats
        try:
            latest_stats = ContractorStat.objects.filter(contractor=contractor).latest('date')
            stats_serializer = ContractorStatSerializer(latest_stats)
            contractor_stats = stats_serializer.data
        except ContractorStat.DoesNotExist:
            contractor_stats = {
                'date': today,
                'profile_views': 0,
                'appointment_requests': 0,
                'completed_appointments': 0,
                'cancelled_appointments': 0,
                'total_earnings': 0,
                'average_rating': None
            }
        
        # Get 30-day appointment stats
        appointments_30d = Appointment.objects.filter(
            contractor=contractor,
            created_at__gte=thirty_days_ago
        )
        
        appointment_stats = {
            'total': appointments_30d.count(),
            'requested': appointments_30d.filter(status='REQUESTED').count(),
            'confirmed': appointments_30d.filter(status='CONFIRMED').count(),
            'completed': appointments_30d.filter(status='COMPLETED').count(),
            'cancelled': appointments_30d.filter(status='CANCELLED').count()
        }
        
        # Get payment stats
        payment_stats = Payment.objects.filter(
            contractor=contractor,
            created_at__gte=thirty_days_ago
        ).aggregate(
            total_earnings=Sum('amount'),
            completed_count=Count('id', filter=models.Q(status='COMPLETED')),
            pending_count=Count('id', filter=models.Q(status='PENDING'))
        )
        
        # Get rating stats
        rating_stats = contractor.reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            contractor=contractor,
            appointment_date__gte=today,
            status__in=['REQUESTED', 'CONFIRMED']
        ).order_by('appointment_date', 'start_time')[:5]
        
        upcoming_appointments_data = [
            {
                'id': appointment.id,
                'client_name': appointment.client.name,
                'date': appointment.appointment_date,
                'start_time': appointment.start_time,
                'status': appointment.status
            }
            for appointment in upcoming_appointments
        ]
        
        return Response({
            'contractor_stats': contractor_stats,
            'appointment_stats': appointment_stats,
            'payment_stats': {
                'total_earnings': payment_stats.get('total_earnings', 0) if payment_stats.get('total_earnings') else 0,
                'completed_count': payment_stats.get('completed_count', 0),
                'pending_count': payment_stats.get('pending_count', 0)
            },
            'rating_stats': {
                'avg_rating': rating_stats.get('avg_rating'),
                'total_reviews': rating_stats.get('total_reviews', 0)
            },
            'upcoming_appointments': upcoming_appointments_data
        })
    
    @action(detail=False, methods=['get'])
    def client_dashboard(self, request):
        """Get client-specific dashboard data"""
        # Check if user is a client
        if hasattr(request.user, 'contractor_profile'):
            return Response(
                {'detail': 'This endpoint is for clients only.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        
        # Get appointment stats
        appointment_stats = Appointment.objects.filter(client=request.user).aggregate(
            total=Count('id'),
            requested=Count('id', filter=models.Q(status='REQUESTED')),
            confirmed=Count('id', filter=models.Q(status='CONFIRMED')),
            completed=Count('id', filter=models.Q(status='COMPLETED')),
            cancelled=Count('id', filter=models.Q(status='CANCELLED'))
        )
        
        # Get payment stats
        payment_stats = Payment.objects.filter(client=request.user).aggregate(
            total_spent=Sum('amount'),
            completed_count=Count('id', filter=models.Q(status='COMPLETED')),
            pending_count=Count('id', filter=models.Q(status='PENDING'))
        )
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            client=request.user,
            appointment_date__gte=today,
            status__in=['REQUESTED', 'CONFIRMED']
        ).order_by('appointment_date', 'start_time')[:5]
        
        upcoming_appointments_data = [
            {
                'id': appointment.id,
                'contractor_name': appointment.contractor.business_name,
                'date': appointment.appointment_date,
                'start_time': appointment.start_time,
                'status': appointment.status
            }
            for appointment in upcoming_appointments
        ]
        
        # Get recent contractors worked with
        recent_contractors = ContractorProfile.objects.filter(
            contractor_appointments__client=request.user
        ).distinct().order_by('-contractor_appointments__created_at')[:5]
        
        recent_contractors_data = [
            {
                'id': contractor.id,
                'business_name': contractor.business_name,
                'services': [category.name for category in contractor.service_categories.all()[:3]]
            }
            for contractor in recent_contractors
        ]
        
        return Response({
            'appointment_stats': appointment_stats,
            'payment_stats': {
                'total_spent': payment_stats.get('total_spent', 0) if payment_stats.get('total_spent') else 0,
                'completed_count': payment_stats.get('completed_count', 0),
                'pending_count': payment_stats.get('pending_count', 0)
            },
            'upcoming_appointments': upcoming_appointments_data,
            'recent_contractors': recent_contractors_data
        })
