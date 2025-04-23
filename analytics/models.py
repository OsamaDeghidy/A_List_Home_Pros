from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from contractors.models import ContractorProfile, ServiceCategory


class DashboardStat(TimeStampedModel):
    """Statistics for dashboard display"""
    date = models.DateField()
    new_users = models.IntegerField(default=0)
    new_contractors = models.IntegerField(default=0)
    new_appointments = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    total_payment_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'
    
    def __str__(self):
        return f"Stats for {self.date}"


class ContractorStat(TimeStampedModel):
    """Statistics for individual contractors"""
    contractor = models.ForeignKey(
        ContractorProfile,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    date = models.DateField()
    profile_views = models.IntegerField(default=0)
    appointment_requests = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    cancelled_appointments = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['contractor', 'date']
    
    def __str__(self):
        return f"Stats for {self.contractor.business_name} on {self.date}"


class ServiceCategoryStat(TimeStampedModel):
    """Statistics for service categories"""
    service_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    date = models.DateField()
    contractor_count = models.IntegerField(default=0)
    appointment_count = models.IntegerField(default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['service_category', 'date']
    
    def __str__(self):
        return f"Stats for {self.service_category.name} on {self.date}"


class UserActivity(TimeStampedModel):
    """Track user activity on the platform"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"


class SearchQuery(TimeStampedModel):
    """Track search queries on the platform"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries'
    )
    query = models.TextField()
    filters = models.JSONField(default=dict, blank=True)
    results_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Search queries'
    
    def __str__(self):
        return f"Search: {self.query[:30]}... ({self.results_count} results)"
