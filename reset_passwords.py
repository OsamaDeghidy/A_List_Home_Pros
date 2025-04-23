#!/usr/bin/env python
"""
Script to reset passwords for users in the A-List Home Pros platform
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def reset_passwords():
    """Reset passwords for all users based on their roles"""
    print("\n=== Resetting User Passwords ===\n")
    print("{:<30} {:<20} {:<15} {:<20}".format("Email", "Name", "Role", "New Password"))
    print("-" * 85)
    
    # Password mapping by role
    password_map = {
        'admin': 'admin123',
        'client': 'client123',
        'contractor': 'contractor123',
        'crew': 'crew123',
        'specialist': 'specialist123'
    }
    
    with transaction.atomic():
        for user in User.objects.all():
            # Get password based on user role
            password = password_map.get(user.role.lower(), 'password123')
            
            # Set new password
            user.set_password(password)
            user.save()
            
            print("{:<30} {:<20} {:<15} {:<20}".format(
                user.email,
                user.name[:18] if user.name else "",
                user.role,
                password
            ))
    
    print("\nAll passwords have been reset successfully.")
    print("You can now use these passwords to authenticate with the API.")

if __name__ == "__main__":
    reset_passwords()
