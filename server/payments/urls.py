from django.urls import path
from .views import (
    StripeOnboardingView,
    StripeAccountStatusView,
    PaymentCreateView,
    PaymentListView,
    PaymentDetailView,
    stripe_webhook,
    stripe_dashboard_link
)

urlpatterns = [
    # Stripe Connect onboarding for A-List Home Pros
    path('onboard/', StripeOnboardingView.as_view(), name='stripe-onboarding'),
    path('status/', StripeAccountStatusView.as_view(), name='stripe-account-status'),
    path('dashboard-link/', stripe_dashboard_link, name='stripe-dashboard-link'),
    
    # Payments
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    
    # Webhook
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
