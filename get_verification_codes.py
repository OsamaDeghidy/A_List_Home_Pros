#!/usr/bin/env python
"""
Verification Code Generator for A-List Home Pros Platform

This script generates and displays verification codes for all users except admin.
"""

import os
import sys
import django
import random
import string
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from users.models import UserRole, EmailVerification
from django.utils import timezone

User = get_user_model()


def generate_verification_code(length=20):
    """Generate a random verification code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_verification_codes():
    """Get verification codes for all users except admin"""
    print("\n=== Verification Codes for All Users (except Admin) ===\n")
    print("{:<30} {:<20} {:<30} {:<20}".format("Email", "Name", "Role", "Verification Code"))
    print("-" * 100)
    
    # Get all users except admin
    users = User.objects.exclude(role=UserRole.ADMIN)
    
    if not users.exists():
        print("No users found in the database (excluding admin).")
        return
    
    for user in users:
        # Check if user has email verification
        try:
            verification = EmailVerification.objects.get(user=user)
            # Check if verification is expired
            if verification.expires_at < timezone.now():
                # Create new verification code
                verification.token = generate_verification_code()
                verification.expires_at = timezone.now() + timedelta(days=7)
                verification.save()
            code = verification.token
        except EmailVerification.DoesNotExist:
            # Create new verification
            code = generate_verification_code()
            expires_at = timezone.now() + timedelta(days=7)
            verification = EmailVerification.objects.create(
                user=user,
                token=code,
                expires_at=expires_at
            )
        
        print("{:<30} {:<20} {:<30} {:<20}".format(
            user.email, 
            user.name[:20], 
            user.role, 
            code
        ))
    
    print("\n=== SMS Verification Codes ===\n")
    
    # Check if notifications app is installed
    try:
        from notifications.models import SMSVerification
        
        # Get all SMS verifications
        sms_verifications = SMSVerification.objects.all()
        
        if sms_verifications.exists():
            print("{:<30} {:<20} {:<20} {:<20}".format("Phone Number", "User Email", "Verification Code", "Expires At"))
            print("-" * 100)
            
            for verification in sms_verifications:
                print("{:<30} {:<20} {:<20} {:<20}".format(
                    verification.phone_number,
                    verification.user.email[:20],
                    verification.verification_code,
                    verification.expires_at.strftime('%Y-%m-%d %H:%M:%S')
                ))
        else:
            print("No SMS verifications found.")
    except ImportError:
        print("Notifications app not installed or SMS verification not implemented.")


def create_test_users():
    """Create test users if none exist"""
    print("\nCreating test users...\n")
    
    # Check if admin exists
    try:
        admin = User.objects.get(email="admin@alistpros.com")
        print(f"Admin user already exists: {admin.email}")
    except User.DoesNotExist:
        # Create admin user
        admin = User.objects.create_user(
            email="admin@alistpros.com",
            name="Admin User",
            phone_number="1234567890",
            password="admin123",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        print(f"Created admin user: {admin.email}")
    
    # Create client users
    client_data = [
        {"email": "client1@example.com", "name": "John Client", "phone": "2345678901"},
        {"email": "client2@example.com", "name": "Sarah Client", "phone": "2345678902"},
        {"email": "client3@example.com", "name": "Mike Client", "phone": "2345678903"},
    ]
    
    for data in client_data:
        try:
            client = User.objects.get(email=data["email"])
            print(f"Client user already exists: {client.email}")
        except User.DoesNotExist:
            client = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                phone_number=data["phone"],
                password="client123",
                role=UserRole.CLIENT
            )
            print(f"Created client user: {client.email}")
    
    # Create contractor users
    contractor_data = [
        {"email": "contractor1@example.com", "name": "Bob Contractor", "phone": "3456789001"},
        {"email": "contractor2@example.com", "name": "Alice Contractor", "phone": "3456789002"},
        {"email": "contractor3@example.com", "name": "Dave Contractor", "phone": "3456789003"},
    ]
    
    for data in contractor_data:
        try:
            contractor = User.objects.get(email=data["email"])
            print(f"Contractor user already exists: {contractor.email}")
        except User.DoesNotExist:
            contractor = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                phone_number=data["phone"],
                password="contractor123",
                role=UserRole.CONTRACTOR
            )
            print(f"Created contractor user: {contractor.email}")


if __name__ == "__main__":
    print("A-List Home Pros Verification Code Generator")
    
    # Create test users
    create_test_users()
    
    # Get verification codes
    get_verification_codes()
