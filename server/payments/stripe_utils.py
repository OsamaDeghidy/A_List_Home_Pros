import stripe
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import StripeAccount, Payment, PaymentStatus

# Initialize Stripe with the API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_account(user):
    """
    Create a Stripe Connect Express account for a user
    """
    try:
        # Create the account
        account = stripe.Account.create(
            type="express",
            country="US",
            email=user.email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="individual",
            business_profile={
                "mcc": "1520",  # General Contractors
                "url": "https://www.alistpros.com",
            },
        )
        
        # Create the account record in our database
        stripe_account = StripeAccount.objects.create(
            user=user,
            stripe_account_id=account.id
        )
        
        return stripe_account
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        print(f"Stripe error: {str(e)}")
        raise e


def generate_account_link(stripe_account, request=None):
    """
    Generate an account link for onboarding
    """
    try:
        # Generate a return URL
        base_url = "https://www.alistpros.com"
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        
        refresh_url = f"{base_url}/onboarding/refresh"
        return_url = f"{base_url}/onboarding/complete"
        
        # Create the account link
        account_link = stripe.AccountLink.create(
            account=stripe_account.stripe_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )
        
        # Update the onboarding URL in our database
        stripe_account.onboarding_url = account_link.url
        stripe_account.save()
        
        return account_link.url
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        print(f"Stripe error: {str(e)}")
        raise e


def check_account_status(stripe_account):
    """
    Check the status of a Stripe account
    """
    try:
        account = stripe.Account.retrieve(stripe_account.stripe_account_id)
        
        # Update the account status in our database
        stripe_account.is_details_submitted = account.details_submitted
        stripe_account.is_charges_enabled = account.charges_enabled
        stripe_account.is_payouts_enabled = account.payouts_enabled
        stripe_account.save()
        
        # If the account is fully onboarded, update the contractor profile
        if account.details_submitted and account.charges_enabled:
            if hasattr(stripe_account.user, 'contractor_profile'):
                contractor_profile = stripe_account.user.contractor_profile
                contractor_profile.is_onboarded = True
                contractor_profile.save()
        
        return {
            'details_submitted': account.details_submitted,
            'charges_enabled': account.charges_enabled,
            'payouts_enabled': account.payouts_enabled
        }
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        print(f"Stripe error: {str(e)}")
        raise e


def create_payment_intent(client, contractor, amount, description):
    """
    Create a payment intent for a client to pay a contractor
    """
    try:
        # Check if the contractor has a Stripe account
        if not hasattr(contractor.user, 'stripe_account'):
            raise ValueError("Contractor does not have a Stripe account")
        
        stripe_account = contractor.user.stripe_account
        
        # Check if the contractor's Stripe account is ready to accept payments
        if not stripe_account.is_charges_enabled:
            raise ValueError("Contractor's Stripe account is not ready to accept payments")
        
        # Create the payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            description=description,
            application_fee_amount=int(amount * 0.1 * 100),  # 10% platform fee
            transfer_data={
                "destination": stripe_account.stripe_account_id,
            },
            metadata={
                "client_id": client.id,
                "contractor_id": contractor.id,
            },
        )
        
        # Create the payment record in our database
        payment = Payment.objects.create(
            client=client,
            contractor=contractor,
            amount=amount,
            description=description,
            stripe_payment_intent_id=payment_intent.id,
            status=PaymentStatus.PENDING
        )
        
        return {
            'payment': payment,
            'client_secret': payment_intent.client_secret
        }
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        print(f"Stripe error: {str(e)}")
        raise e


def handle_payment_intent_succeeded(event):
    """
    Handle the payment_intent.succeeded webhook event
    """
    payment_intent = event.data.object
    
    try:
        # Find the payment in our database
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent.id)
        
        # Update the payment status
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = timezone.now()
        payment.save()
        
        return payment
    except Payment.DoesNotExist:
        print(f"Payment not found for payment intent: {payment_intent.id}")
        return None


def handle_account_updated(event):
    """
    Handle the account.updated webhook event
    """
    account = event.data.object
    
    try:
        # Find the Stripe account in our database
        stripe_account = StripeAccount.objects.get(stripe_account_id=account.id)
        
        # Update the account status
        stripe_account.is_details_submitted = account.details_submitted
        stripe_account.is_charges_enabled = account.charges_enabled
        stripe_account.is_payouts_enabled = account.payouts_enabled
        stripe_account.save()
        
        # If the account is fully onboarded, update the contractor profile
        if account.details_submitted and account.charges_enabled:
            if hasattr(stripe_account.user, 'contractor_profile'):
                contractor_profile = stripe_account.user.contractor_profile
                contractor_profile.is_onboarded = True
                contractor_profile.save()
        
        return stripe_account
    except StripeAccount.DoesNotExist:
        print(f"Stripe account not found: {account.id}")
        return None
