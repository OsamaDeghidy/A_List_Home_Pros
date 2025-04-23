#!/usr/bin/env python
"""
Script to check if user passwords are valid
"""

import os
import django
import getpass

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

def check_password(email, password):
    """Check if password is valid for a user"""
    user = authenticate(email=email, password=password)
    if user is not None:
        return True
    return False

def check_all_passwords():
    """Check passwords for predefined users"""
    print("\n=== Password Check ===\n")
    print("{:<30} {:<20} {:<15}".format("Email", "Password", "Valid"))
    print("-" * 65)
    
    # List of users and their expected passwords
    users_to_check = [
        {"email": "admin@alistpros.com", "password": "admin123"},
        {"email": "client1@example.com", "password": "client123"},
        {"email": "contractor1@example.com", "password": "contractor123"},
        {"email": "crew1@example.com", "password": "crew123"},
        {"email": "specialist1@example.com", "password": "specialist123"}
    ]
    
    for user_data in users_to_check:
        email = user_data["email"]
        password = user_data["password"]
        
        valid = check_password(email, password)
        status = "Valid" if valid else "Invalid"
        
        print("{:<30} {:<20} {:<15}".format(
            email,
            password,
            status
        ))

if __name__ == "__main__":
    check_all_passwords()
