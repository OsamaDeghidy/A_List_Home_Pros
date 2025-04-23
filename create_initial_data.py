#!/usr/bin/env python
"""
Initial Data Creation Script for A-List Home Pros Platform

This script creates the initial data needed for the A-List Home Pros platform
including service categories, admin user, and test users.
"""

import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from users.models import UserRole
from contractors.models import ServiceCategory, ContractorProfile, ContractorPortfolio, ContractorReview
from scheduling.models import AvailabilitySlot, UnavailableDate
from notifications.models import Notification, SMSVerification

User = get_user_model()

def create_service_categories():
    """Create service categories"""
    print("\n=== Creating Service Categories ===\n")
    
    categories = [
        "Plumbing", "Electrical", "HVAC", "Carpentry", "Painting", 
        "Landscaping", "Cleaning", "Roofing", "Flooring", 
        "General Contracting", "Handyman", "Appliance Repair"
    ]
    
    for category_name in categories:
        category, created = ServiceCategory.objects.get_or_create(name=category_name)
        if created:
            print(f"Created: {category_name}")
        else:
            print(f"Already exists: {category_name}")

def create_users():
    """Create admin, clients, contractors, crew members, and specialists"""
    print("\n=== Creating Users ===\n")
    
    # Admin user
    admin_email = "admin@alistpros.com"
    admin, created = User.objects.get_or_create(
        email=admin_email,
        defaults={
            'name': 'Admin User',
            'phone_number': '555-123-4567',
            'role': UserRole.ADMIN,
            'is_staff': True,
            'is_superuser': True,
            'email_verified': True
        }
    )
    
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Created admin: {admin_email}")
    else:
        print(f"Admin already exists: {admin_email}")
    
    # Client users
    clients = [
        {'email': 'client1@example.com', 'name': 'John Client', 'phone': '555-111-1111'},
        {'email': 'client2@example.com', 'name': 'Sarah Client', 'phone': '555-222-2222'},
        {'email': 'client3@example.com', 'name': 'Mike Client', 'phone': '555-333-3333'},
        {'email': 'client4@example.com', 'name': 'Emma Client', 'phone': '555-444-4444'},
        {'email': 'client5@example.com', 'name': 'David Client', 'phone': '555-555-5555'},
    ]
    
    for client_data in clients:
        client, created = User.objects.get_or_create(
            email=client_data['email'],
            defaults={
                'name': client_data['name'],
                'phone_number': client_data['phone'],
                'role': UserRole.CLIENT,
                'email_verified': True
            }
        )
        
        if created:
            client.set_password('client123')
            client.save()
            print(f"Created client: {client_data['email']}")
        else:
            print(f"Client already exists: {client_data['email']}")
    
    # Contractor users
    contractors = [
        {'email': 'contractor1@example.com', 'name': 'Bob Contractor', 'phone': '555-666-6666'},
        {'email': 'contractor2@example.com', 'name': 'Alice Contractor', 'phone': '555-777-7777'},
        {'email': 'contractor3@example.com', 'name': 'Dave Contractor', 'phone': '555-888-8888'},
        {'email': 'contractor4@example.com', 'name': 'Linda Contractor', 'phone': '555-999-9999'},
        {'email': 'contractor5@example.com', 'name': 'Mark Contractor', 'phone': '555-000-0000'},
    ]
    
    contractor_users = []
    for contractor_data in contractors:
        contractor, created = User.objects.get_or_create(
            email=contractor_data['email'],
            defaults={
                'name': contractor_data['name'],
                'phone_number': contractor_data['phone'],
                'role': UserRole.CONTRACTOR,
                'email_verified': True
            }
        )
        
        if created:
            contractor.set_password('contractor123')
            contractor.save()
            print(f"Created contractor: {contractor_data['email']}")
        else:
            print(f"Contractor already exists: {contractor_data['email']}")
        
        contractor_users.append(contractor)
    
    # Crew members
    crew_members = [
        {'email': 'crew1@example.com', 'name': 'Mike Crew', 'phone': '555-101-1010'},
        {'email': 'crew2@example.com', 'name': 'Taylor Crew', 'phone': '555-202-2020'},
        {'email': 'crew3@example.com', 'name': 'Jordan Crew', 'phone': '555-303-3030'},
    ]
    
    for crew_data in crew_members:
        crew, created = User.objects.get_or_create(
            email=crew_data['email'],
            defaults={
                'name': crew_data['name'],
                'phone_number': crew_data['phone'],
                'role': UserRole.CREW,
                'email_verified': True
            }
        )
        
        if created:
            crew.set_password('crew123')
            crew.save()
            print(f"Created crew member: {crew_data['email']}")
        else:
            print(f"Crew member already exists: {crew_data['email']}")
    
    # Specialists
    specialists = [
        {'email': 'specialist1@example.com', 'name': 'Lisa Specialist', 'phone': '555-404-4040'},
        {'email': 'specialist2@example.com', 'name': 'Casey Specialist', 'phone': '555-505-5050'},
    ]
    
    for specialist_data in specialists:
        specialist, created = User.objects.get_or_create(
            email=specialist_data['email'],
            defaults={
                'name': specialist_data['name'],
                'phone_number': specialist_data['phone'],
                'role': UserRole.SPECIALIST,
                'email_verified': True
            }
        )
        
        if created:
            specialist.set_password('specialist123')
            specialist.save()
            print(f"Created specialist: {specialist_data['email']}")
        else:
            print(f"Specialist already exists: {specialist_data['email']}")
    
    return contractor_users

def create_contractor_profiles(contractors):
    """Create contractor profiles for contractor users"""
    print("\n=== Creating Contractor Profiles ===\n")
    
    categories = list(ServiceCategory.objects.all())
    
    for contractor in contractors:
        profile, created = ContractorProfile.objects.get_or_create(
            user=contractor,
            defaults={
                'business_name': f"{contractor.name}'s Services",
                'business_description': f"Professional services provided by {contractor.name}. Quality work guaranteed.",
                'years_of_experience': random.randint(3, 20),
                'license_number': f"LIC-{random.randint(10000, 99999)}",
                'insurance_info': f"Insured up to ${random.randint(1, 5)}M",
                'service_radius': random.randint(10, 50),
                'is_onboarded': True,
            }
        )
        
        if created:
            # Add 2-4 random service categories
            num_categories = random.randint(2, 4)
            selected_categories = random.sample(categories, num_categories)
            profile.service_categories.add(*selected_categories)
            print(f"Created contractor profile for: {contractor.email}")
        else:
            print(f"Contractor profile already exists for: {contractor.email}")

def create_portfolio_items(contractors):
    """Create portfolio items for contractors"""
    print("\n=== Creating Portfolio Items ===\n")
    
    for contractor in contractors:
        profile = ContractorProfile.objects.get(user=contractor)
        
        # Create 2-3 portfolio items for each contractor
        num_items = random.randint(2, 3)
        
        for i in range(1, num_items + 1):
            item, created = ContractorPortfolio.objects.get_or_create(
                contractor=profile,
                title=f"Project {i} for {contractor.name}",
                defaults={
                    'description': f"A completed project by {contractor.name}. Client was very satisfied with the results.",
                    'completion_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                }
            )
            
            if created:
                print(f"Created portfolio item: {item.title}")

def create_reviews(contractors):
    """Create reviews for contractors"""
    print("\n=== Creating Reviews ===\n")
    
    clients = User.objects.filter(role=UserRole.CLIENT)
    
    # Clear existing reviews to avoid duplicates
    ContractorReview.objects.all().delete()
    print("Cleared existing reviews")
    
    for contractor in contractors:
        profile = ContractorProfile.objects.get(user=contractor)
        
        # Create 2-3 reviews for each contractor
        num_reviews = random.randint(2, 3)
        selected_clients = random.sample(list(clients), num_reviews)
        
        for client in selected_clients:
            rating = random.randint(3, 5)  # Only create good reviews (3-5 stars)
            
            review = ContractorReview.objects.create(
                contractor=profile,
                client=client,
                rating=rating,
                comment=f"{'Excellent' if rating == 5 else 'Good' if rating == 4 else 'Satisfactory'} work done by {contractor.name}. {'Would highly recommend!' if rating == 5 else 'Recommended.' if rating == 4 else ''}",
                is_verified=True,
            )
            
            print(f"Created review: {rating} stars from {client.name} for {contractor.name}")

def create_availability(contractors):
    """Create availability schedules for contractors"""
    print("\n=== Creating Availability Schedules ===\n")
    
    days_of_week = [0, 1, 2, 3, 4, 5, 6]  # Monday to Sunday
    
    # Clear existing availability slots to avoid duplicates
    AvailabilitySlot.objects.all().delete()
    UnavailableDate.objects.all().delete()
    print("Cleared existing availability data")
    
    for contractor in contractors:
        # Get contractor profile
        profile = ContractorProfile.objects.get(user=contractor)
        
        # Each contractor is available on 4-7 days of the week
        num_available_days = random.randint(4, 7)
        available_days = random.sample(days_of_week, num_available_days)
        
        for day in available_days:
            # Random start and end times
            start_hour = random.randint(7, 10)
            end_hour = random.randint(16, 19)
            
            availability = AvailabilitySlot.objects.create(
                contractor=profile,
                day_of_week=day,
                start_time=f"{start_hour:02d}:00",
                end_time=f"{end_hour:02d}:00",
                is_recurring=True
            )
            
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day]
            print(f"Created availability: {day_name} {start_hour:02d}:00 - {end_hour:02d}:00 for {contractor.name}")
        
        # Add some unavailable dates
        if random.choice([True, False]):
            # Random date in the next 60 days
            unavailable_date = datetime.now() + timedelta(days=random.randint(1, 60))
            unavailable_date = unavailable_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Create unavailable date
            UnavailableDate.objects.create(
                contractor=profile,
                date=unavailable_date.date(),
                reason='Personal day off'
            )
            
            print(f"Created unavailable date: {unavailable_date.strftime('%Y-%m-%d')} for {contractor.name}")

def create_notifications(users):
    """Create sample notifications for users"""
    print("\n=== Creating Notifications ===\n")
    
    # Clear existing notifications to avoid duplicates
    Notification.objects.all().delete()
    SMSVerification.objects.all().delete()
    print("Cleared existing notifications and SMS verifications")
    
    notification_types = [
        'APPOINTMENT',
        'MESSAGE',
        'PAYMENT',
        'MARKETING',
    ]
    
    for user in users:
        # Create 2-3 random notifications for each user
        num_notifications = random.randint(2, 3)
        
        for _ in range(num_notifications):
            notification_type = random.choice(notification_types)
            
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=f"{notification_type.title()} Notification",
                message=f"This is a {notification_type.lower()} notification for {user.name}.",
                read=random.choice([True, False])
            )
            
            print(f"Created {notification_type} notification for {user.name}")
                
        # Create SMS verification for some users
        if random.choice([True, False]) and user.phone_number:
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expires_at = datetime.now() + timedelta(minutes=10)
            
            sms_verification = SMSVerification.objects.create(
                user=user,
                phone_number=user.phone_number,
                verification_code=verification_code,
                expires_at=expires_at,
                is_verified=random.choice([True, False])
            )
            
            print(f"Created SMS verification code for {user.name}: {verification_code}")

def main():
    """Main function to create all initial data"""
    print("A-List Home Pros Initial Data Creation")
    
    # Create service categories
    create_service_categories()
    
    # Create users
    contractors = create_users()
    
    # Create contractor profiles
    create_contractor_profiles(contractors)
    
    # Create portfolio items
    create_portfolio_items(contractors)
    
    # Create reviews
    create_reviews(contractors)
    
    # Create availability schedules
    create_availability(contractors)
    
    # Create notifications
    all_users = User.objects.all()
    create_notifications(all_users)
    
    print("\n=== Initial Data Creation Complete ===\n")
    print("You can now log in with the following credentials:")
    print("Admin: admin@alistpros.com / admin123")
    print("Client: client1@example.com / client123")
    print("Contractor: contractor1@example.com / contractor123")

if __name__ == "__main__":
    main()
