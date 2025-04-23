from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class ServiceCategory(TimeStampedModel):
    """
    Categories of services offered by contractors
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Service Categories'


class ContractorProfile(TimeStampedModel):
    """
    Extended profile information for contractors
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contractor_profile')
    business_name = models.CharField(max_length=255)
    business_description = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    license_number = models.CharField(max_length=100, blank=True)
    insurance_info = models.CharField(max_length=255, blank=True)
    service_radius = models.PositiveIntegerField(default=50, help_text='Service radius in miles')
    profile_image = models.ImageField(upload_to='contractor_profiles/', blank=True, null=True)
    is_onboarded = models.BooleanField(default=False)
    service_categories = models.ManyToManyField(ServiceCategory, related_name='contractors')
    
    def __str__(self):
        return f"{self.business_name} - {self.user.email}"


class ContractorPortfolio(TimeStampedModel):
    """
    Portfolio items for contractors to showcase their work
    """
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='contractor_portfolio/')
    completion_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.title


class ContractorReview(TimeStampedModel):
    """
    Reviews for contractors left by clients
    """
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveSmallIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Review for {self.contractor.business_name} by {self.client.name}"
