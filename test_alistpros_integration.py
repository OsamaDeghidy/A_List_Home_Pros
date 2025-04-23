#!/usr/bin/env python
"""
Test script for A-List Home Pros integration.
This script tests the integration of the A-List Home Pros features with the rest of the project.
It creates test data and verifies that the API endpoints work as expected.
"""

import os
import sys
import json
import requests
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from users.models import UserRole
from alistpros_profiles.models import AListHomeProProfile, ServiceCategory, AListHomeProPortfolio as Portfolio, AListHomeProReview as Review
from notifications.models import Notification, NotificationSetting
from payments.models import AListHomeProStripeAccount, Payment

User = get_user_model()

# Test server URL
BASE_URL = "http://localhost:8000/api"
# Store tokens
tokens = {}

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

def create_test_users():
    """Create test users with different roles."""
    print_header("Creating Test Users")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email="admin@alistpros.com",
        defaults={
            "name": "Admin User",
            "phone_number": "+1234567890",
            "role": UserRole.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        }
    )
    if created:
        admin_user.set_password("admin123")
        admin_user.save()
        print_success(f"Created admin user: {admin_user.email}")
    else:
        print_info(f"Admin user already exists: {admin_user.email}")
    
    # Create client user
    client_user, created = User.objects.get_or_create(
        email="client1@example.com",
        defaults={
            "name": "Client User",
            "phone_number": "+1987654321",
            "role": UserRole.CLIENT,
        }
    )
    if created:
        client_user.set_password("client123")
        client_user.save()
        print_success(f"Created client user: {client_user.email}")
    else:
        print_info(f"Client user already exists: {client_user.email}")
    
    # Create A-List Home Pro user
    alistpro_user, created = User.objects.get_or_create(
        email="alistpro1@example.com",
        defaults={
            "name": "A-List Home Pro User",
            "phone_number": "+1122334455",
            "role": UserRole.CONTRACTOR,  # Using CONTRACTOR role as it's been renamed to A-List Home Pro
        }
    )
    if created:
        alistpro_user.set_password("alistpro123")
        alistpro_user.save()
        print_success(f"Created A-List Home Pro user: {alistpro_user.email}")
    else:
        print_info(f"A-List Home Pro user already exists: {alistpro_user.email}")
    
    return {
        "admin": admin_user,
        "client": client_user,
        "alistpro": alistpro_user
    }

def create_service_categories():
    """Create service categories for A-List Home Pros."""
    print_header("Creating Service Categories")
    
    categories = [
        {"name": "Plumbing", "description": "Water systems, pipes, fixtures"},
        {"name": "Electrical", "description": "Wiring, lighting, electrical systems"},
        {"name": "Carpentry", "description": "Woodworking, framing, cabinetry"},
        {"name": "Painting", "description": "Interior and exterior painting"},
        {"name": "Landscaping", "description": "Lawn care, gardening, outdoor spaces"},
    ]
    
    created_categories = []
    for category_data in categories:
        category, created = ServiceCategory.objects.get_or_create(
            name=category_data["name"],
            defaults={"description": category_data["description"]}
        )
        if created:
            print_success(f"Created service category: {category.name}")
        else:
            print_info(f"Service category already exists: {category.name}")
        created_categories.append(category)
    
    return created_categories

def create_alistpro_profile(user, categories):
    """Create an A-List Home Pro profile."""
    print_header("Creating A-List Home Pro Profile")
    
    profile, created = AListHomeProProfile.objects.get_or_create(
        user=user,
        defaults={
            "business_name": "Quality Home Services",
            "business_description": "Professional home improvement and repair services",
            "years_of_experience": 10,
            "license_number": "LIC-12345",
            "insurance_info": "Fully insured with liability coverage",
            "service_radius": 50,
            "average_rating": 4.8,
        }
    )
    
    if created:
        # Add service categories
        profile.service_categories.add(*categories[:3])  # Add first 3 categories
        print_success(f"Created A-List Home Pro profile for: {user.email}")
    else:
        print_info(f"A-List Home Pro profile already exists for: {user.email}")
    
    # Create portfolio items
    portfolio_items = [
        {
            "title": "Kitchen Renovation",
            "description": "Complete kitchen remodel with custom cabinets",
            "completion_date": "2024-01-15",
        },
        {
            "title": "Bathroom Remodel",
            "description": "Modern bathroom renovation with walk-in shower",
            "completion_date": "2024-02-20",
        }
    ]
    
    for item_data in portfolio_items:
        portfolio, created = Portfolio.objects.get_or_create(
            alistpro=profile,
            title=item_data["title"],
            defaults={
                "description": item_data["description"],
                "completion_date": datetime.strptime(item_data["completion_date"], "%Y-%m-%d").date(),
            }
        )
        if created:
            print_success(f"Created portfolio item: {portfolio.title}")
        else:
            print_info(f"Portfolio item already exists: {portfolio.title}")
    
    return profile

def create_reviews(client_user, alistpro_profile):
    """Create reviews for an A-List Home Pro."""
    print_header("Creating Reviews")
    
    reviews = [
        {
            "rating": 5,
            "comment": "Excellent service! Very professional and completed the work on time.",
        },
        {
            "rating": 4,
            "comment": "Good work quality, slightly delayed but communicated well.",
        }
    ]
    
    for review_data in reviews:
        review, created = Review.objects.get_or_create(
            client=client_user,
            alistpro=alistpro_profile,
            rating=review_data["rating"],
            defaults={
                "comment": review_data["comment"],
            }
        )
        if created:
            print_success(f"Created review with rating: {review.rating}")
        else:
            print_info(f"Review already exists with rating: {review.rating}")

def create_notifications(users):
    """Create notifications for users."""
    print_header("Creating Notifications")
    
    notifications = [
        {
            "user": users["admin"],
            "type": "SYSTEM",
            "title": "System Update",
            "message": "The system has been updated with new features.",
        },
        {
            "user": users["client"],
            "type": "ALISTPRO_VERIFICATION",
            "title": "New A-List Home Pro Available",
            "message": "A new A-List Home Pro has been verified in your area.",
        },
        {
            "user": users["alistpro"],
            "type": "ALISTPRO_ONBOARDING",
            "title": "Complete Your Profile",
            "message": "Please complete your A-List Home Pro profile to start receiving job requests.",
        }
    ]
    
    for notif_data in notifications:
        notification, created = Notification.objects.get_or_create(
            user=notif_data["user"],
            type=notif_data["type"],
            title=notif_data["title"],
            defaults={
                "message": notif_data["message"],
                "is_read": False,
            }
        )
        if created:
            print_success(f"Created notification for {notif_data['user'].email}: {notification.title}")
        else:
            print_info(f"Notification already exists for {notif_data['user'].email}: {notification.title}")
    
    # Create notification settings
    for user in users.values():
        settings, created = NotificationSetting.objects.get_or_create(
            user=user,
            defaults={
                "email_enabled": True,
                "sms_enabled": user.role == UserRole.CLIENT,  # Enable SMS for clients only
                "push_enabled": True,
            }
        )
        if created:
            print_success(f"Created notification settings for: {user.email}")
        else:
            print_info(f"Notification settings already exist for: {user.email}")

def test_authentication_api():
    """Test authentication API endpoints."""
    print_header("Testing Authentication API")
    
    # Test login endpoint
    users = [
        {"email": "admin@alistpros.com", "password": "admin123", "role": "admin"},
        {"email": "client1@example.com", "password": "client123", "role": "client"},
        {"email": "alistpro1@example.com", "password": "alistpro123", "role": "alistpro"},
    ]
    
    for user in users:
        response = requests.post(
            f"{BASE_URL}/users/login/",
            json={"email": user["email"], "password": user["password"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            tokens[user["role"]] = {
                "access": data.get("access"),
                "refresh": data.get("refresh"),
            }
            print_success(f"Login successful for {user['role']}: {user['email']}")
        else:
            print_error(f"Login failed for {user['role']}: {user['email']}")
            print_info(f"Response: {response.status_code} - {response.text}")
    
    # Test user profile endpoint
    for role, token in tokens.items():
        response = requests.get(
            f"{BASE_URL}/users/me/",
            headers={"Authorization": f"Bearer {token['access']}"}
        )
        
        if response.status_code == 200:
            print_success(f"Profile retrieval successful for {role}")
        else:
            print_error(f"Profile retrieval failed for {role}")
            print_info(f"Response: {response.status_code} - {response.text}")

def test_alistpros_api():
    """Test A-List Home Pros API endpoints."""
    print_header("Testing A-List Home Pros API")
    
    # Test list all A-List Home Pros
    response = requests.get(f"{BASE_URL}/alistpros/profiles/")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data)} A-List Home Pro profiles")
    else:
        print_error("Failed to retrieve A-List Home Pro profiles")
        print_info(f"Response: {response.status_code} - {response.text}")
    
    # Test service categories endpoint
    response = requests.get(f"{BASE_URL}/alistpros/services/")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data)} service categories")
    else:
        print_error("Failed to retrieve service categories")
        print_info(f"Response: {response.status_code} - {response.text}")

def test_notifications_api():
    """Test notifications API endpoints."""
    print_header("Testing Notifications API")
    
    for role, token in tokens.items():
        response = requests.get(
            f"{BASE_URL}/notifications/notifications/",
            headers={"Authorization": f"Bearer {token['access']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} notifications for {role}")
        else:
            print_error(f"Failed to retrieve notifications for {role}")
            print_info(f"Response: {response.status_code} - {response.text}")
    
    # Test notification settings endpoint
    for role, token in tokens.items():
        response = requests.get(
            f"{BASE_URL}/notifications/settings/",
            headers={"Authorization": f"Bearer {token['access']}"}
        )
        
        if response.status_code == 200:
            print_success(f"Retrieved notification settings for {role}")
        else:
            print_error(f"Failed to retrieve notification settings for {role}")
            print_info(f"Response: {response.status_code} - {response.text}")

def main():
    """Main function to run all tests."""
    print_header("A-List Home Pros Integration Test")
    
    try:
        # Create test data
        users = create_test_users()
        categories = create_service_categories()
        alistpro_profile = create_alistpro_profile(users["alistpro"], categories)
        create_reviews(users["client"], alistpro_profile)
        create_notifications(users)
        
        # Test API endpoints
        test_authentication_api()
        test_alistpros_api()
        test_notifications_api()
        
        print_header("Test Summary")
        print_success("All test data created successfully!")
        print_info("You can now use the API with the following credentials:")
        print_info("Admin: admin@alistpros.com / admin123")
        print_info("Client: client1@example.com / client123")
        print_info("A-List Home Pro: alistpro1@example.com / alistpro123")
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
