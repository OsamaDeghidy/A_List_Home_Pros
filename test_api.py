#!/usr/bin/env python
"""
API Testing Script for A-List Home Pros Platform

This script tests the main API endpoints of the A-List Home Pros platform,
including user registration, authentication, contractor profiles, and reviews.
It also provides verification codes for all users except admin.
"""

import requests
import json
import sys
import time
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from users.models import UserRole, EmailVerification
from django.utils import timezone
from datetime import timedelta
import random
import string

User = get_user_model()

# Base URL for API
BASE_URL = "http://localhost:8000/api"

# Test data
CLIENT_USER = {
    "email": "client@example.com",
    "name": "Test Client",
    "phone_number": "1234567890",
    "password": "SecurePass123!",
    "role": "CLIENT"
}


def generate_verification_code(length=20):
    """
    Generate a random verification code
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_verification_codes():
    """
    Get verification codes for all users except admin
    """
    print("\n=== Verification Codes for All Users (except Admin) ===\n")
    print("{:<30} {:<20} {:<30} {:<20}".format("Email", "Name", "Role", "Verification Code"))
    print("-" * 100)
    
    # Get all users except admin
    users = User.objects.exclude(role=UserRole.ADMIN)
    
    if not users.exists():
        print("No users found in the database (excluding admin).")
        return
    
    # Use raw SQL to avoid ORM issues with the table structure
    from django.db import connection
    
    for user in users:
        # Check if user has email verification
        with connection.cursor() as cursor:
            cursor.execute("SELECT token, expires_at FROM users_emailverification WHERE user_id = %s", [user.id])
            verification = cursor.fetchone()
            
            if verification:
                token, expires_at_str = verification
                # Parse the expires_at string to a datetime object
                try:
                    # Try parsing ISO format
                    expires_at = timezone.datetime.fromisoformat(expires_at_str)
                except ValueError:
                    # If that fails, try a different format
                    expires_at = timezone.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S.%f")
                
                # Check if verification is expired
                if expires_at < timezone.now():
                    # Create new verification code
                    new_token = generate_verification_code()
                    new_expires_at = (timezone.now() + timedelta(days=7))
                    cursor.execute(
                        "UPDATE users_emailverification SET token = %s, expires_at = %s WHERE user_id = %s",
                        [new_token, new_expires_at.isoformat(), user.id]
                    )
                    code = new_token
                else:
                    code = token
            else:
                # Create new verification
                code = generate_verification_code()
                expires_at = timezone.now() + timedelta(days=7)
                cursor.execute(
                    "INSERT INTO users_emailverification (user_id, token, expires_at) VALUES (%s, %s, %s)",
                    [user.id, code, expires_at.isoformat()]
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


# Main function
def main():
    """
    Main function to run the tests
    """
    # Get verification codes
    get_verification_codes()


# Run the script
if __name__ == "__main__":
    main()

CONTRACTOR_USER = {
    "email": "contractor@example.com",
    "name": "Test Contractor",
    "phone_number": "0987654321",
    "password": "SecurePass123!",
    "role": "CONTRACTOR"
}

CONTRACTOR_PROFILE = {
    "business_name": "Test Construction LLC",
    "description": "We are a test construction company",
    "years_in_business": 5,
    "license_number": "TEST-12345",
    "insurance_info": "Fully insured",
    "service_area": "Test City and surrounding areas"
}

REVIEW_DATA = {
    "rating": 4,
    "comment": "Great work, very professional!",
}

SERVICE_CATEGORY = {
    "name": "Plumbing",
    "description": "All plumbing services"
}

# Store tokens and IDs
tokens = {
    "client": None,
    "contractor": None
}

ids = {
    "contractor_profile": None,
    "service_category": None,
    "review": None
}

def print_response(response, label):
    """Print formatted response for debugging"""
    print(f"\n--- {label} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)
    return response.json() if response.status_code < 400 else None

def test_register_users():
    """Test user registration for both client and contractor"""
    print("\n=== Testing User Registration ===")
    
    # Register client
    response = requests.post(f"{BASE_URL}/users/register/", json=CLIENT_USER)
    print_response(response, "Client Registration")
    
    # Register contractor
    response = requests.post(f"{BASE_URL}/users/register/", json=CONTRACTOR_USER)
    print_response(response, "Contractor Registration")
    
    return True

def test_login():
    """Test login and JWT token acquisition"""
    print("\n=== Testing User Login ===")
    
    # Login as client
    response = requests.post(f"{BASE_URL}/users/token/", json={
        "email": CLIENT_USER["email"],
        "password": CLIENT_USER["password"]
    })
    result = print_response(response, "Client Login")
    if result:
        tokens["client"] = result["access"]
    
    # Login as contractor
    response = requests.post(f"{BASE_URL}/users/token/", json={
        "email": CONTRACTOR_USER["email"],
        "password": CONTRACTOR_USER["password"]
    })
    result = print_response(response, "Contractor Login")
    if result:
        tokens["contractor"] = result["access"]
    
    return tokens["client"] is not None and tokens["contractor"] is not None

def test_create_service_category():
    """Test creating a service category (admin function)"""
    print("\n=== Testing Service Category Creation ===")
    
    # Use contractor token (normally admin would do this)
    headers = {"Authorization": f"Bearer {tokens['contractor']}"}
    
    response = requests.post(
        f"{BASE_URL}/contractors/service-categories/",
        json=SERVICE_CATEGORY,
        headers=headers
    )
    result = print_response(response, "Create Service Category")
    
    if result:
        ids["service_category"] = result["id"]
    
    return ids["service_category"] is not None

def test_create_contractor_profile():
    """Test creating a contractor profile"""
    print("\n=== Testing Contractor Profile Creation ===")
    
    if not ids["service_category"]:
        print("Service category ID not available. Skipping profile creation.")
        return False
    
    # Create profile data with service category
    profile_data = CONTRACTOR_PROFILE.copy()
    profile_data["service_categories"] = [ids["service_category"]]
    
    headers = {"Authorization": f"Bearer {tokens['contractor']}"}
    
    response = requests.post(
        f"{BASE_URL}/contractors/profiles/",
        json=profile_data,
        headers=headers
    )
    result = print_response(response, "Create Contractor Profile")
    
    if result:
        ids["contractor_profile"] = result["id"]
    
    return ids["contractor_profile"] is not None

def test_update_contractor_profile():
    """Test updating a contractor profile"""
    print("\n=== Testing Contractor Profile Update ===")
    
    if not ids["contractor_profile"]:
        print("Contractor profile ID not available. Skipping profile update.")
        return False
    
    update_data = {
        "business_name": "Updated Construction LLC",
        "description": "We are an updated test construction company"
    }
    
    headers = {"Authorization": f"Bearer {tokens['contractor']}"}
    
    response = requests.patch(
        f"{BASE_URL}/contractors/profiles/{ids['contractor_profile']}/",
        json=update_data,
        headers=headers
    )
    print_response(response, "Update Contractor Profile")
    
    return response.status_code == 200

def test_create_review():
    """Test creating a review for a contractor"""
    print("\n=== Testing Review Creation ===")
    
    if not ids["contractor_profile"]:
        print("Contractor profile ID not available. Skipping review creation.")
        return False
    
    review_data = REVIEW_DATA.copy()
    review_data["contractor"] = ids["contractor_profile"]
    
    headers = {"Authorization": f"Bearer {tokens['client']}"}
    
    response = requests.post(
        f"{BASE_URL}/contractors/reviews/",
        json=review_data,
        headers=headers
    )
    result = print_response(response, "Create Review")
    
    if result:
        ids["review"] = result["id"]
    
    return ids["review"] is not None

def test_get_contractor_profiles():
    """Test getting all contractor profiles"""
    print("\n=== Testing Get All Contractor Profiles ===")
    
    response = requests.get(f"{BASE_URL}/contractors/profiles/")
    print_response(response, "Get All Contractor Profiles")
    
    return response.status_code == 200

def test_get_contractor_profile_detail():
    """Test getting a specific contractor profile"""
    print("\n=== Testing Get Contractor Profile Detail ===")
    
    if not ids["contractor_profile"]:
        print("Contractor profile ID not available. Skipping profile detail.")
        return False
    
    response = requests.get(f"{BASE_URL}/contractors/profiles/{ids['contractor_profile']}/")
    print_response(response, "Get Contractor Profile Detail")
    
    return response.status_code == 200

def run_all_tests():
    """Run all API tests in sequence"""
    tests = [
        ("User Registration", test_register_users),
        ("User Login", test_login),
        ("Service Category Creation", test_create_service_category),
        ("Contractor Profile Creation", test_create_contractor_profile),
        ("Contractor Profile Update", test_update_contractor_profile),
        ("Review Creation", test_create_review),
        ("Get All Contractor Profiles", test_get_contractor_profiles),
        ("Get Contractor Profile Detail", test_get_contractor_profile_detail)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'=' * 20} RUNNING TEST: {name} {'=' * 20}")
        try:
            success = test_func()
            results.append((name, "PASSED" if success else "FAILED"))
        except Exception as e:
            print(f"Error during {name}: {str(e)}")
            results.append((name, "ERROR"))
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Print summary
    print("\n\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    for name, result in results:
        status_color = "\033[92m" if result == "PASSED" else "\033[91m"  # Green for pass, red for fail
        print(f"{name}: {status_color}{result}\033[0m")
    print("=" * 60)

if __name__ == "__main__":
    print("A-List Home Pros API Testing")
    print("Make sure the Django server is running on http://localhost:8000")
    input("Press Enter to start testing...")
    run_all_tests()
