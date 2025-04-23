from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel

# Import both models to support backward compatibility during transition
try:
    from alistpros_profiles.models import AListHomeProProfile
    USE_NEW_MODEL = True
except ImportError:
    from contractors.models import ContractorProfile
    USE_NEW_MODEL = False


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class Payment(TimeStampedModel):
    """
    Model to track payments between clients and A-List Home Pros
    """
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_made')
    # Use a string reference to avoid circular import issues
    alistpro = models.ForeignKey('alistpros_profiles.AListHomeProProfile', on_delete=models.CASCADE, 
                                 related_name='payments_received', null=True, blank=True)
    # Keep contractor field for backward compatibility
    contractor = models.ForeignKey('contractors.ContractorProfile', on_delete=models.CASCADE, 
                                   related_name='payments_received_old', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_transfer_id = models.CharField(max_length=255, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        if self.alistpro:
            pro_name = self.alistpro.business_name
        elif self.contractor:
            pro_name = self.contractor.business_name
        else:
            pro_name = "Unknown Pro"
        return f"Payment of ${self.amount} from {self.client.name} to {pro_name}"


class AListHomeProStripeAccount(TimeStampedModel):
    """
    Model to track Stripe Connect Express accounts for A-List Home Pros
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alistpro_stripe_account')
    stripe_account_id = models.CharField(max_length=255)
    is_details_submitted = models.BooleanField(default=False)
    is_charges_enabled = models.BooleanField(default=False)
    is_payouts_enabled = models.BooleanField(default=False)
    onboarding_url = models.TextField(blank=True, null=True)
    onboarding_complete = models.BooleanField(default=False)
    onboarding_started_at = models.DateTimeField(auto_now_add=True)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)
    last_webhook_received_at = models.DateTimeField(null=True, blank=True)
    last_webhook_type = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Stripe account for {self.user.email}"
    
    def mark_onboarding_complete(self):
        """Mark the onboarding process as complete"""
        self.onboarding_complete = True
        self.onboarding_completed_at = timezone.now()
        self.save(update_fields=['onboarding_complete', 'onboarding_completed_at'])
    
    def update_webhook_received(self, webhook_type):
        """Update the last webhook received information"""
        self.last_webhook_received_at = timezone.now()
        self.last_webhook_type = webhook_type
        self.save(update_fields=['last_webhook_received_at', 'last_webhook_type'])


# Keep the old model name as a proxy for backward compatibility
class StripeAccount(AListHomeProStripeAccount):
    class Meta:
        proxy = True
