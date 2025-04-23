"""
Email verification functionality for the A-List Home Pros platform.
"""
import secrets
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import timedelta

from .models import EmailVerification


def generate_verification_token():
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)


def send_verification_email(user):
    """
    Send a verification email to the user.
    
    Args:
        user: The user to send the verification email to.
        
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    # Create or update verification token
    verification, created = EmailVerification.objects.update_or_create(
        user=user,
        defaults={
            'token': generate_verification_token(),
            'expires_at': timezone.now() + timedelta(days=3)
        }
    )
    
    # Build verification URL
    verification_url = f"{settings.SITE_URL}/api/users/verify-email/{verification.token}/"
    
    # Prepare email content
    context = {
        'user': user,
        'verification_url': verification_url,
        'expiration_days': 3,
    }
    
    html_message = render_to_string('users/email_verification.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject='Verify Your Email - A-List Home Pros',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def verify_email_token(token):
    """
    Verify an email verification token.
    
    Args:
        token: The token to verify.
        
    Returns:
        user: The user associated with the token if valid, None otherwise.
    """
    try:
        verification = EmailVerification.objects.get(token=token)
        
        # Check if token is expired
        if verification.expires_at < timezone.now():
            return None
        
        # Mark user as verified
        user = verification.user
        user.email_verified = True
        user.save()
        
        # Delete the verification token
        verification.delete()
        
        return user
    except EmailVerification.DoesNotExist:
        return None
