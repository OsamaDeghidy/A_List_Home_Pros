#!/usr/bin/env python
"""
API Endpoint Testing Script for A-List Home Pros Platform

This script tests the main API endpoints of the A-List Home Pros platform
to ensure they are working correctly with the test data, particularly
focusing on the changes from "Contractor" to "A-List Home Pro".
"""

import requests
import json
import sys
import os
from datetime import datetime

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

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message."""
    print(f"ℹ️ {message}")

def print_response(response, label="Response"):
    """Print formatted response for debugging"""
    print(f"\n--- {label} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-------------------")

def get_auth_token(credentials):
    """Get JWT auth token for a user"""
    url = f"{BASE_URL}/users/token/"
    response = requests.post(url, json=credentials)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Login successful for {credentials['email']}")
        return data.get("access")
    else:
        print_error(f"Login failed for {credentials['email']}")
        print_info(f"Response: {response.status_code} - {response.text}")
        return None

def test_user_profile(token):
    """Test getting user profile"""
    url = f"{BASE_URL}/users/me/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print_success("User profile retrieved successfully")
    else:
        print_error("Failed to retrieve user profile")
    print_response(response, "User Profile")
    return response.status_code == 200

def test_alistpro_profiles():
    """Test getting all A-List Home Pro profiles"""
    # Try the new endpoint first
    url = f"{BASE_URL}/alistpros/profiles/"
    response = requests.get(url)
    if response.status_code == 200:
        print_success("Retrieved A-List Home Pro profiles successfully")
        print_response(response, "All A-List Home Pro Profiles")
        return True
    else:
        # Fall back to the old endpoint for backward compatibility
        url = f"{BASE_URL}/contractors/profiles/"
        response = requests.get(url)
        if response.status_code == 200:
            print_success("Retrieved Contractor profiles successfully (Legacy Endpoint)")
        else:
            print_error("Failed to retrieve profiles from both endpoints")
        print_response(response, "All Contractor Profiles (Legacy Endpoint)")
        return response.status_code == 200

def test_alistpro_profile_detail(alistpro_id=1):
    """Test getting a specific A-List Home Pro profile"""
    # Try the new endpoint first
    url = f"{BASE_URL}/alistpros/profiles/{alistpro_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        print_success(f"Retrieved A-List Home Pro profile {alistpro_id} successfully")
        print_response(response, f"A-List Home Pro Profile {alistpro_id}")
        return True
    else:
        # Fall back to the old endpoint for backward compatibility
        url = f"{BASE_URL}/contractors/profiles/{alistpro_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            print_success(f"Retrieved Contractor profile {alistpro_id} successfully (Legacy Endpoint)")
        else:
            print_error(f"Failed to retrieve profile {alistpro_id} from both endpoints")
        print_response(response, f"Contractor Profile {alistpro_id} (Legacy Endpoint)")
        return response.status_code == 200

def test_appointments(token):
    """Test getting appointments"""
    url = f"{BASE_URL}/scheduling/appointments/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print_success("Appointments retrieved successfully")
    else:
        print_error("Failed to retrieve appointments")
    print_response(response, "Appointments")
    return response.status_code == 200

def test_conversations(token):
    """Test getting conversations"""
    url = f"{BASE_URL}/messaging/conversations/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print_success("Conversations retrieved successfully")
    else:
        print_error("Failed to retrieve conversations")
    print_response(response, "Conversations")
    return response.status_code == 200

def test_notifications(token):
    """Test getting notifications"""
    url = f"{BASE_URL}/notifications/notifications/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print_success("Notifications retrieved successfully")
    else:
        print_error("Failed to retrieve notifications")
    print_response(response, "Notifications")
    return response.status_code == 200

def test_stripe_dashboard_link(token):
    """Test getting Stripe dashboard link"""
    url = f"{BASE_URL}/payments/dashboard-link/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print_success("Stripe dashboard link retrieved successfully")
    else:
        print_error("Failed to retrieve Stripe dashboard link")
    print_response(response, "Stripe Dashboard Link")
    return response.status_code == 200

def main():
    """Main function to run all tests"""
    print_header("A-List Home Pros API Testing")
    print_info("Make sure the Django server is running on http://localhost:8000")
    
    results = {}
    total_tests = 0
    passed_tests = 0

    # Authentication tests
    print_header("Authentication Tests")
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
    print_header("User Profile Tests")
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
    print_header("A-List Home Pro Profile Tests")
    results["All A-List Home Pro Profiles"] = test_alistpro_profiles()
    total_tests += 1
    passed_tests += 1 if results["All A-List Home Pro Profiles"] else 0

    results["A-List Home Pro Profile Detail"] = test_alistpro_profile_detail()
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Profile Detail"] else 0
    
    # Stripe integration test
    print_header("Stripe Integration Tests")
    results["Stripe Dashboard Link"] = test_stripe_dashboard_link(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["Stripe Dashboard Link"] else 0

    # Appointment tests
    print_header("Appointment Tests")
    results["Admin Appointments"] = test_appointments(admin_token)
    total_tests += 1
    passed_tests += 1 if results["Admin Appointments"] else 0

    results["Client Appointments"] = test_appointments(client_token)
    total_tests += 1
    passed_tests += 1 if results["Client Appointments"] else 0

    results["A-List Home Pro Appointments"] = test_appointments(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Appointments"] else 0

    # Conversation tests
    print_header("Conversation Tests")
    results["Admin Conversations"] = test_conversations(admin_token)
    total_tests += 1
    passed_tests += 1 if results["Admin Conversations"] else 0

    results["Client Conversations"] = test_conversations(client_token)
    total_tests += 1
    passed_tests += 1 if results["Client Conversations"] else 0

    results["A-List Home Pro Conversations"] = test_conversations(alistpro_token)
    total_tests += 1
    passed_tests += 1 if results["A-List Home Pro Conversations"] else 0

    # Notification tests
    print_header("Notification Tests")
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
    print_header("Test Results")
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print_header("Test Summary")
    print_info(f"Total Tests: {total_tests}")
    print_info(f"Passed Tests: {passed_tests}")
    print_info(f"Failed Tests: {total_tests - passed_tests}")
    print_info(f"Success Rate: {success_rate:.2f}%")
    
    if passed_tests == total_tests:
        print_success("All tests passed! The A-List Home Pro integration is working correctly.")
    else:
        print_error("Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
