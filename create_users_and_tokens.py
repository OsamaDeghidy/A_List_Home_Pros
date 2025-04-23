#!/usr/bin/env python
"""
Script to create test users and verification tokens
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


def create_test_users():
    """Create test users directly using SQL to avoid model field issues"""
    print("\n=== Creating Test Users ===\n")
    
    # Test user data
    users = [
        # Clients
        {
            'email': 'client1@example.com',
            'name': 'John Client',
            'phone_number': '1234567890',
            'password': 'pbkdf2_sha256$600000$5UWyuALbHvLGZQbCcB3Vr0$j+3kQOEJrS9e+SqUqyI2c8NhRQZ3+gcvcnOz7JG9dWw=',  # client123
            'role': 'client',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'email': 'client2@example.com',
            'name': 'Sarah Client',
            'phone_number': '2345678901',
            'password': 'pbkdf2_sha256$600000$5UWyuALbHvLGZQbCcB3Vr0$j+3kQOEJrS9e+SqUqyI2c8NhRQZ3+gcvcnOz7JG9dWw=',  # client123
            'role': 'client',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        },
        # Contractors
        {
            'email': 'contractor1@example.com',
            'name': 'Bob Contractor',
            'phone_number': '3456789012',
            'password': 'pbkdf2_sha256$600000$5UWyuALbHvLGZQbCcB3Vr0$j+3kQOEJrS9e+SqUqyI2c8NhRQZ3+gcvcnOz7JG9dWw=',  # client123
            'role': 'contractor',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        },
        {
            'email': 'contractor2@example.com',
            'name': 'Alice Contractor',
            'phone_number': '4567890123',
            'password': 'pbkdf2_sha256$600000$5UWyuALbHvLGZQbCcB3Vr0$j+3kQOEJrS9e+SqUqyI2c8NhRQZ3+gcvcnOz7JG9dWw=',  # client123
            'role': 'contractor',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        },
        # Crew
        {
            'email': 'crew1@example.com',
            'name': 'Mike Crew',
            'phone_number': '5678901234',
            'password': 'pbkdf2_sha256$600000$5UWyuALbHvLGZQbCcB3Vr0$j+3kQOEJrS9e+SqUqyI2c8NhRQZ3+gcvcnOz7JG9dWw=',  # client123
            'role': 'crew',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        },
        # Specialist
        {
            'email': 'specialist1@example.com',
            'name': 'Lisa Specialist',
            'phone_number': '6789012345',
            'password': 'pbkdf2_sha256$600000$5UWyuALbHvLGZQbCcB3Vr0$j+3kQOEJrS9e+SqUqyI2c8NhRQZ3+gcvcnOz7JG9dWw=',  # client123
            'role': 'specialist',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
    ]
    
    with connection.cursor() as cursor:
        for user in users:
            # Check if user already exists
            cursor.execute("SELECT id FROM users_customuser WHERE email = %s", [user['email']])
            if cursor.fetchone():
                print(f"User already exists: {user['email']}")
                continue
            
            # Create user
            cursor.execute("""
                INSERT INTO users_customuser (
                    email, name, phone_number, password, role, 
                    is_active, is_staff, is_superuser, date_joined, is_verified
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, [
                user['email'], user['name'], user['phone_number'], user['password'], user['role'],
                user['is_active'], user['is_staff'], user['is_superuser'], timezone.now(), True
            ])
            
            user_id = cursor.fetchone()[0]
            print(f"Created user: {user['email']} (ID: {user_id})")


def create_verification_tokens():
    """Create verification tokens for all users"""
    print("\n=== Creating Verification Tokens for All Users (except Admin) ===\n")
    print("{:<30} {:<20} {:<15} {:<40}".format("Email", "Name", "Role", "Verification Token"))
    print("-" * 105)
    
    # Get all non-admin users
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, email, name, role 
            FROM users_customuser 
            WHERE role != 'admin'
        """)
        users = cursor.fetchall()
    
    if not users:
        print("No users found in the database (excluding admin).")
        return
    
    for user_id, email, name, role in users:
        # Generate a new verification token
        token = generate_verification_code()
        expires_at = timezone.now() + timedelta(days=7)
        
        # Check if user already has a verification token
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users_emailverification WHERE user_id = %s", [user_id])
            verification = cursor.fetchone()
            
            if verification:
                # Update existing token
                cursor.execute("""
                    UPDATE users_emailverification 
                    SET token = %s, expires_at = %s 
                    WHERE user_id = %s
                """, [token, expires_at, user_id])
                status = "Updated"
            else:
                # Create new token
                cursor.execute("""
                    INSERT INTO users_emailverification (user_id, token, expires_at) 
                    VALUES (%s, %s, %s)
                """, [user_id, token, expires_at])
                status = "Created"
        
        print("{:<30} {:<20} {:<15} {:<40} ({})".format(
            email,
            name[:18] if name else "",
            role,
            token,
            status
        ))


if __name__ == "__main__":
    print("A-List Home Pros User and Verification Token Generator")
    create_test_users()
    create_verification_tokens()
