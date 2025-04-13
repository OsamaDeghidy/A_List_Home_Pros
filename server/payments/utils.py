import stripe
import json
import logging
from django.conf import settings
from django.urls import reverse
from .models import AListHomeProStripeAccount

logger = logging.getLogger(__name__)

# Configure Stripe with the API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_account(user):
    """
    Create a Stripe Connect Express account for an A-List Home Pro
    
    Args:
        user: The user to create the account for
        
    Returns:
        The created AListHomeProStripeAccount instance
    """
    try:
        # Check if the user already has a Stripe account
        try:
            stripe_account = AListHomeProStripeAccount.objects.get(user=user)
            logger.info(f"User {user.email} already has a Stripe account: {stripe_account.stripe_account_id}")
            return stripe_account
        except AListHomeProStripeAccount.DoesNotExist:
            pass
        
        # Create a new Stripe Connect Express account
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
                "mcc": "1711",  # Heating, Plumbing, A/C
                "url": settings.SITE_URL,
            },
            metadata={
                "user_id": str(user.id),
                "email": user.email,
            }
        )
        
        # Create the AListHomeProStripeAccount instance
        stripe_account = AListHomeProStripeAccount.objects.create(
            user=user,
            stripe_account_id=account.id,
        )
        
        logger.info(f"Created Stripe account {account.id} for user {user.email}")
        return stripe_account
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating account for {user.email}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating Stripe account for {user.email}: {str(e)}")
        raise

def generate_account_link(stripe_account, refresh_url, return_url):
    """
    Generate an account link for onboarding a Stripe Connect Express account
    
    Args:
        stripe_account: The AListHomeProStripeAccount instance
        refresh_url: URL to redirect to if the link expires
        return_url: URL to redirect to after onboarding
        
    Returns:
        The account link URL
    """
    try:
        account_link = stripe.AccountLink.create(
            account=stripe_account.stripe_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )
        
        # Update the onboarding URL
        stripe_account.onboarding_url = account_link.url
        stripe_account.save(update_fields=['onboarding_url'])
        
        return account_link.url
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error generating account link: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating account link: {str(e)}")
        raise

def handle_account_updated_webhook(event_data):
    """
    Handle the account.updated webhook event from Stripe
    
    Args:
        event_data: The webhook event data
        
    Returns:
        The updated AListHomeProStripeAccount instance or None
    """
    try:
        account = event_data['data']['object']
        account_id = account['id']
        
        # Find the corresponding AListHomeProStripeAccount
        try:
            stripe_account = AListHomeProStripeAccount.objects.get(stripe_account_id=account_id)
        except AListHomeProStripeAccount.DoesNotExist:
            logger.warning(f"Received account.updated webhook for unknown account: {account_id}")
            return None
        
        # Update account details
        stripe_account.is_details_submitted = account.get('details_submitted', False)
        stripe_account.is_charges_enabled = account.get('charges_enabled', False)
        stripe_account.is_payouts_enabled = account.get('payouts_enabled', False)
        
        # Check if onboarding is complete
        if (stripe_account.is_details_submitted and 
            stripe_account.is_charges_enabled and 
            stripe_account.is_payouts_enabled and
            not stripe_account.onboarding_complete):
            stripe_account.mark_onboarding_complete()
        
        stripe_account.update_webhook_received('account.updated')
        stripe_account.save()
        
        logger.info(f"Updated Stripe account {account_id} for user {stripe_account.user.email}")
        return stripe_account
        
    except Exception as e:
        logger.error(f"Error handling account.updated webhook: {str(e)}")
        raise

def create_payment_intent(client, alistpro, amount, description):
    """
    Create a payment intent for a client to pay an A-List Home Pro
    
    Args:
        client: The client user
        alistpro: The A-List Home Pro profile
        amount: The payment amount in dollars
        description: The payment description
        
    Returns:
        The created payment intent
    """
    try:
        # Get the A-List Home Pro's Stripe account
        try:
            stripe_account = AListHomeProStripeAccount.objects.get(user=alistpro.user)
        except AListHomeProStripeAccount.DoesNotExist:
            logger.error(f"A-List Home Pro {alistpro.user.email} does not have a Stripe account")
            raise ValueError("A-List Home Pro does not have a Stripe account")
        
        # Check if the account is ready to accept payments
        if not stripe_account.is_charges_enabled:
            logger.error(f"A-List Home Pro {alistpro.user.email} cannot accept payments yet")
            raise ValueError("A-List Home Pro cannot accept payments yet")
        
        # Convert amount to cents
        amount_cents = int(amount * 100)
        
        # Calculate application fee (platform fee)
        application_fee = int(amount_cents * settings.PLATFORM_FEE_PERCENTAGE)
        
        # Create the payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            description=description,
            application_fee_amount=application_fee,
            transfer_data={
                "destination": stripe_account.stripe_account_id,
            },
            metadata={
                "client_id": str(client.id),
                "client_email": client.email,
                "alistpro_id": str(alistpro.id),
                "alistpro_email": alistpro.user.email,
            }
        )
        
        return payment_intent
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise


def get_stripe_dashboard_link(stripe_account_id):
    """
    Generate a link to the Stripe dashboard for an A-List Home Pro
    
    Args:
        stripe_account_id: The Stripe account ID
        
    Returns:
        The dashboard link URL
    """
    try:
        # Create a login link for the connected account
        login_link = stripe.Account.create_login_link(
            stripe_account_id
        )
        
        return login_link.url
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating dashboard link: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating dashboard link: {str(e)}")
        raise
