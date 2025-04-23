#!/usr/bin/env python
"""
Script to fix the user model by adding the missing email_verified column
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.db import connection


def fix_user_model():
    """Add email_verified column to users_customuser table if it doesn't exist"""
    print("\n=== Fixing User Model ===\n")
    
    with connection.cursor() as cursor:
        # Check if email_verified column exists
        cursor.execute("PRAGMA table_info(users_customuser)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email_verified' in columns:
            print("Column 'email_verified' already exists in users_customuser table.")
        else:
            # Add email_verified column
            cursor.execute("""
                ALTER TABLE users_customuser 
                ADD COLUMN email_verified BOOLEAN DEFAULT 0
            """)
            print("Added 'email_verified' column to users_customuser table.")
            
            # Update email_verified based on is_verified
            cursor.execute("""
                UPDATE users_customuser 
                SET email_verified = is_verified
            """)
            print("Updated 'email_verified' values based on 'is_verified'.")


if __name__ == "__main__":
    print("A-List Home Pros User Model Fixer")
    fix_user_model()
