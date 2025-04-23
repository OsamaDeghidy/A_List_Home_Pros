#!/usr/bin/env python
"""
Script to show verification codes for all users in the A-List Home Pros platform
"""

import os
import django
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from users.models import UserRole

User = get_user_model()


def show_verification_codes():
    """Show verification codes for all users except admin"""
    print("\n=== Verification Codes for All Users (except Admin) ===\n")
    print("{:<30} {:<20} {:<15} {:<40}".format("Email", "Name", "Role", "Verification Code"))
    print("-" * 105)
    
    # Get all non-admin users
    users = User.objects.exclude(role=UserRole.ADMIN)
    
    if not users.exists():
        print("No users found in the database (excluding admin).")
        return
    
    # Get verification codes from the database
    with connection.cursor() as cursor:
        for user in users:
            cursor.execute("""
                SELECT token FROM users_emailverification 
                WHERE user_id = %s
            """, [user.id])
            
            result = cursor.fetchone()
            verification_code = result[0] if result else "No verification code"
            
            print("{:<30} {:<20} {:<15} {:<40}".format(
                user.email,
                user.name[:18] if user.name else "",
                user.role,
                verification_code
            ))
    
    print("\n=== SMS Verification Codes ===\n")
    
    # Check if notifications app is installed and SMSVerification model exists
    try:
        # Get all SMS verifications
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.email, u.name, sv.phone_number, sv.verification_code
                FROM notifications_smsverification sv
                JOIN users_customuser u ON sv.user_id = u.id
            """)
            
            results = cursor.fetchall()
            
            if results:
                print("{:<30} {:<20} {:<15} {:<10}".format(
                    "Email", "Name", "Phone", "Code"
                ))
                print("-" * 75)
                
                for email, name, phone, code in results:
                    print("{:<30} {:<20} {:<15} {:<10}".format(
                        email,
                        name[:18] if name else "",
                        phone,
                        code
                    ))
            else:
                print("No SMS verification codes found.")
    except Exception as e:
        print(f"Error retrieving SMS verification codes: {e}")


if __name__ == "__main__":
    print("A-List Home Pros Verification Codes")
    show_verification_codes()
