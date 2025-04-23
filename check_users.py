#!/usr/bin/env python
"""
Script to check users in the database and their passwords
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model

User = get_user_model()

def check_users():
    """Check all users in the database"""
    print("\n=== Users in the Database ===\n")
    print("{:<30} {:<20} {:<15} {:<15}".format("Email", "Name", "Role", "Is Active"))
    print("-" * 80)
    
    users = User.objects.all()
    
    if not users.exists():
        print("No users found in the database.")
        return
    
    for user in users:
        print("{:<30} {:<20} {:<15} {:<15}".format(
            user.email,
            user.name[:18] if user.name else "",
            user.role,
            "Yes" if user.is_active else "No"
        ))

if __name__ == "__main__":
    check_users()
