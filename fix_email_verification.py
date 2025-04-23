#!/usr/bin/env python
"""
Script to fix the EmailVerification table in the database
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


def fix_email_verification_table():
    """Fix the EmailVerification table structure and create verification codes for users"""
    print("\n=== Fixing EmailVerification Table ===\n")
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users_emailverification'
        """)
        
        if cursor.fetchone():
            # Drop the existing table
            cursor.execute("DROP TABLE users_emailverification")
            print("Dropped existing users_emailverification table.")
        
        # Create the table with the correct structure
        cursor.execute("""
            CREATE TABLE users_emailverification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                token VARCHAR(100) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users_customuser(id) ON DELETE CASCADE
            )
        """)
        print("Created users_emailverification table with correct structure.")
    
    # Create verification tokens for all users
    create_verification_tokens()


def create_verification_tokens():
    """Create verification tokens for all users except admin"""
    print("\n=== Creating Verification Tokens for All Users (except Admin) ===\n")
    print("{:<30} {:<20} {:<15} {:<40}".format("Email", "Name", "Role", "Verification Token"))
    print("-" * 105)
    
    # Get all non-admin users
    users = User.objects.exclude(role=UserRole.ADMIN)
    
    if not users:
        print("No users found in the database (excluding admin).")
        return
    
    for user in users:
        # Generate a new verification token
        token = generate_verification_code()
        expires_at = timezone.now() + timedelta(days=7)
        
        # Create a new verification token
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO users_emailverification (user_id, token, expires_at) 
                VALUES (%s, %s, %s)
            """, [user.id, token, expires_at])
        
        print("{:<30} {:<20} {:<15} {:<40}".format(
            user.email,
            user.name[:18] if user.name else "",
            user.role,
            token
        ))


if __name__ == "__main__":
    print("A-List Home Pros EmailVerification Table Fixer")
    fix_email_verification_table()
