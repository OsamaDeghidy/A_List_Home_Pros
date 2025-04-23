#!/usr/bin/env python
"""
Script to create verification tokens for all users in the system
"""

import os
import django
import random
import string
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from users.models import UserRole, EmailVerification

User = get_user_model()


def generate_verification_code(length=20):
    """Generate a random verification code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_all_users():
    """Get all users directly from the database to avoid model field issues"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, email, name, role 
            FROM users_customuser 
            WHERE role != 'admin'
        """)
        return cursor.fetchall()


def create_verification_tokens():
    """Create verification tokens for all users"""
    print("\n=== Creating Verification Tokens for All Users (except Admin) ===\n")
    print("{:<30} {:<20} {:<15} {:<40}".format("Email", "Name", "Role", "Verification Token"))
    print("-" * 105)
    
    # Get all non-admin users
    users = get_all_users()
    
    if not users:
        print("No users found in the database (excluding admin).")
        return
    
    for user_id, email, name, role in users:
        # Generate a new verification token
        token = generate_verification_code()
        expires_at = timezone.now() + timedelta(days=7)
        
        # Check if user already has a verification token
        try:
            verification = EmailVerification.objects.get(user_id=user_id)
            verification.token = token
            verification.expires_at = expires_at
            verification.save()
            status = "Updated"
        except EmailVerification.DoesNotExist:
            # Create a new verification token
            EmailVerification.objects.create(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )
            status = "Created"
        
        print("{:<30} {:<20} {:<15} {:<40} ({})".format(
            email,
            name[:18] if name else "",
            role,
            token,
            status
        ))


if __name__ == "__main__":
    print("A-List Home Pros Verification Token Generator")
    create_verification_tokens()
