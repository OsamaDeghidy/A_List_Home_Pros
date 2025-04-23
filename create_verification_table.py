#!/usr/bin/env python
"""
Script to create email verification table and tokens
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


def generate_verification_code(length=20):
    """Generate a random verification code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_verification_table():
    """Create email verification table if it doesn't exist"""
    print("\n=== Creating Email Verification Table ===\n")
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users_emailverification'
        """)
        
        if cursor.fetchone():
            print("Table users_emailverification already exists.")
        else:
            # Create table
            cursor.execute("""
                CREATE TABLE users_emailverification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    token VARCHAR(100) NOT NULL UNIQUE,
                    expires_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users_customuser(id) ON DELETE CASCADE
                )
            """)
            print("Created table users_emailverification.")


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


def show_all_verification_codes():
    """Show all verification codes"""
    print("\n=== All Verification Codes ===\n")
    print("{:<30} {:<20} {:<15} {:<40} {:<20}".format(
        "Email", "Name", "Role", "Verification Token", "Expires At"
    ))
    print("-" * 125)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.email, u.name, u.role, v.token, v.expires_at
            FROM users_emailverification v
            JOIN users_customuser u ON v.user_id = u.id
            ORDER BY u.role, u.email
        """)
        
        verifications = cursor.fetchall()
        
        if not verifications:
            print("No verification codes found.")
            return
        
        for email, name, role, token, expires_at in verifications:
            print("{:<30} {:<20} {:<15} {:<40} {:<20}".format(
                email,
                name[:18] if name else "",
                role,
                token,
                expires_at
            ))


if __name__ == "__main__":
    print("A-List Home Pros Verification Table and Token Generator")
    create_verification_table()
    create_verification_tokens()
    show_all_verification_codes()
