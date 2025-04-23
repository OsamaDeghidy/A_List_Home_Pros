#!/usr/bin/env python
"""
API Endpoint Testing Script for A-List Home Pros Platform

This script tests the main API endpoints of the A-List Home Pros platform
to ensure they are working correctly with the test data.
"""

import requests
import json
import sys
import os

# Base URL for API
BASE_URL = "http://localhost:8000/api"

# Test credentials
ADMIN_USER = {
    "email": "admin@alistpros.com",
    "password": "admin123"
}

CLIENT_USER = {
    "email": "client1@example.com",
    "password": "client123"
}

ALISTPRO_USER = {
    "email": "contractor1@example.com",  # Using existing contractor email for backward compatibility
    "password": "contractor123"
}

def print_response(response, label="Response"):
    """Print formatted response for debugging"""
    print(f"\n=== {label} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Text: {response.text}")
    print("-" * 80)

def get_auth_token(credentials):
    """Get JWT auth token for a user"""
    url = f"{BASE_URL}/users/token/"
    response = requests.post(url, json=credentials)
    
    if response.status_code == 200:
        return response.json().get('access')
    else:
        print_response(response, "Auth Token Error")
        return None

def test_user_profile(token):
    """Test getting user profile"""
    url = f"{BASE_URL}/users/me/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print_response(response, "User Profile")
    return response.status_code == 200

def test_alistpro_profiles():
    """Test getting all A-List Home Pro profiles"""
    # Try the new endpoint first
    url = f"{BASE_URL}/alistpros/profiles/"
    response = requests.get(url)
    if response.status_code == 200:
        print_response(response, "All A-List Home Pro Profiles")
        return True
    else:
        # Fall back to the old endpoint for backward compatibility
        url = f"{BASE_URL}/contractors/profiles/"
        response = requests.get(url)
        print_response(response, "All Contractor Profiles (Legacy Endpoint)")
        return response.status_code == 200

def test_alistpro_profile_detail(alistpro_id=1):
    """Test getting a specific A-List Home Pro profile"""
    # Try the new endpoint first
    url = f"{BASE_URL}/alistpros/profiles/{alistpro_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        print_response(response, f"A-List Home Pro Profile {alistpro_id}")
        return True
    else:
        # Fall back to the old endpoint for backward compatibility
        url = f"{BASE_URL}/contractors/profiles/{alistpro_id}/"
        response = requests.get(url)
        print_response(response, f"Contractor Profile {alistpro_id} (Legacy Endpoint)")
        return response.status_code == 200

def test_appointments(token):
    """Test getting appointments"""
    url = f"{BASE_URL}/scheduling/appointments/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print_response(response, "Appointments")
    return response.status_code == 200

def test_conversations(token):
    """Test getting conversations"""
    url = f"{BASE_URL}/messaging/conversations/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print_response(response, "Conversations")
    return response.status_code == 200

def test_notifications(token):
    """Test getting notifications"""
    url = f"{BASE_URL}/notifications/notifications/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print_response(response, "Notifications")
    return response.status_code == 200

def test_stripe_dashboard_link(token):
    """Test getting Stripe dashboard link"""
    url = f"{BASE_URL}/payments/dashboard-link/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Stripe Dashboard Link")
    return response.status_code == 200

def run_all_tests():
    """Run all API tests"""
    results = {}
    total_tests = 0
    passed_tests = 0

    # Authentication tests
    print("\n=== Authentication Tests ===")
    admin_token = get_auth_token(ADMIN_USER)
    results["Admin Login"] = admin_token is not None
    total_tests += 1
    passed_tests += 1 if results["Admin Login"] else 0

    client_token = get_auth_token(CLIENT_USER)
    results["Client Login"] = client_token is not None
    total_tests += 1
    passed_tests += 1 if results["Client Login"] else 0

    alistpro_token = get_auth_token(ALISTPRO_USER)
    results["A-List Home Pro Login"] = alistpro_token is not None
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Login"] else 0

    # User profile tests
    print("\n=== User Profile Tests ===")
    results["Admin Profile"] = test_user_profile(admin_token)
    total_tests += 1
    passed_tests += 1 if results["Admin Profile"] else 0

    results["Client Profile"] = test_user_profile(client_token)
    total_tests += 1
    passed_tests += 1 if results["Client Profile"] else 0

    results["A-List Home Pro Profile"] = test_user_profile(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Profile"] else 0

    # A-List Home Pro profiles tests
    print("\n=== A-List Home Pro Profile Tests ===")
    results["All A-List Home Pro Profiles"] = test_alistpro_profiles()
    total_tests += 1
    passed_tests += 1 if results["All A-List Home Pro Profiles"] else 0

    results["A-List Home Pro Profile Detail"] = test_alistpro_profile_detail()
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Profile Detail"] else 0
    
    # Stripe integration test
    print("\n=== Stripe Integration Tests ===")
    results["Stripe Dashboard Link"] = test_stripe_dashboard_link(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["Stripe Dashboard Link"] else 0

    # Appointments tests
    print("\n=== Appointments Tests ===")
    results["Admin Appointments"] = test_appointments(admin_token)
    total_tests += 1
    passed_tests += 1 if results["Admin Appointments"] else 0

    results["Client Appointments"] = test_appointments(client_token)
    total_tests += 1
    passed_tests += 1 if results["Client Appointments"] else 0

    results["A-List Home Pro Appointments"] = test_appointments(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Appointments"] else 0

    # Conversations tests
    print("\n=== Conversations Tests ===")
    results["Admin Conversations"] = test_conversations(admin_token)
    total_tests += 1
    passed_tests += 1 if results["Admin Conversations"] else 0

    results["Client Conversations"] = test_conversations(client_token)
    total_tests += 1
    passed_tests += 1 if results["Client Conversations"] else 0

    results["A-List Home Pro Conversations"] = test_conversations(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Conversations"] else 0

    # Notifications tests
    print("\n=== Notifications Tests ===")
    results["Admin Notifications"] = test_notifications(admin_token)
    total_tests += 1
    passed_tests += 1 if results["Admin Notifications"] else 0

    results["Client Notifications"] = test_notifications(client_token)
    total_tests += 1
    passed_tests += 1 if results["Client Notifications"] else 0

    results["A-List Home Pro Notifications"] = test_notifications(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Notifications"] else 0
    
    # Print test results
    print("\n=== Test Results ===")
    for name, test_func in tests:
        print(f"\nRunning test: {name}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"Error: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print("\n=== Test Results Summary ===\n")
    for name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{status} - {name}")
    
    # Calculate success rate
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\nSuccess Rate: {success_rate:.2f}% ({success_count}/{total_count})")
    return success_rate == 100

if __name__ == "__main__":
    print("A-List Home Pros API Endpoint Testing")
    print("Make sure the Django server is running on http://localhost:8000")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/contractors/profiles/")
        if response.status_code >= 500:
            print("Server is running but returning errors. Please check the server logs.")
            sys.exit(1)
    except requests.ConnectionError:
        print("Error: Cannot connect to the server. Please make sure the Django server is running.")
        print("Run: python manage.py runserver")
        sys.exit(1)
    
    # Run tests
    run_all_tests()
