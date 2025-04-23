#!/usr/bin/env python
"""
Test Data Creation Script for A-List Home Pros Platform

This script creates test data for the A-List Home Pros platform
including users, service categories, A-List Home Pro profiles,
portfolios, reviews, appointments, and notifications.
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
from alistpros_profiles.models import ServiceCategory, AListHomeProProfile, AListHomeProPortfolio, AListHomeProReview
from scheduling.models import Appointment, AppointmentStatus
from notifications.models import Notification
from messaging.models import Conversation, Message

User = get_user_model()

def create_users():
    """Create test users with different roles"""
    print("Creating test users...")
    
    # Create admin user if it doesn't exist
    if not User.objects.filter(email='admin@alistpros.com').exists():
        admin = User.objects.create_superuser(
            email='admin@alistpros.com',
            name='Admin User',
            phone_number='555-123-4567',
            password='admin123',
            role=UserRole.ADMIN
        )
        print(f"Created admin user: {admin.email}")
    else:
        admin = User.objects.get(email='admin@alistpros.com')
        print(f"Admin user already exists: {admin.email}")
    
    # Create client users
    client_users = []
    for i in range(1, 4):
        email = f'client{i}@example.com'
        if not User.objects.filter(email=email).exists():
            client = User.objects.create_user(
                email=email,
                name=f'Client User {i}',
                phone_number=f'555-{100+i}-{1000+i}',
                password='client123',
                role=UserRole.CLIENT
            )
            print(f"Created client user: {client.email}")
        else:
            client = User.objects.get(email=email)
            print(f"Client user already exists: {client.email}")
        client_users.append(client)
    
    # Create A-List Home Pro users (contractors)
    alistpro_users = []
    for i in range(1, 4):
        email = f'contractor{i}@example.com'
        if not User.objects.filter(email=email).exists():
            alistpro = User.objects.create_user(
                email=email,
                name=f'A-List Home Pro {i}',
                phone_number=f'555-{200+i}-{2000+i}',
                password='contractor123',
                role=UserRole.CONTRACTOR
            )
            print(f"Created A-List Home Pro user: {alistpro.email}")
        else:
            alistpro = User.objects.get(email=email)
            print(f"A-List Home Pro user already exists: {alistpro.email}")
        alistpro_users.append(alistpro)
    
    return {
        'admin': admin,
        'clients': client_users,
        'alistpros': alistpro_users
    }

def create_service_categories():
    """Create service categories"""
    print("Creating service categories...")
    
    categories = [
        {'name': 'Plumbing', 'description': 'All plumbing services including repairs and installations'},
        {'name': 'Electrical', 'description': 'Electrical installations, repairs, and maintenance'},
        {'name': 'Carpentry', 'description': 'Custom woodworking, furniture, and structural repairs'},
        {'name': 'Painting', 'description': 'Interior and exterior painting services'},
        {'name': 'Landscaping', 'description': 'Garden design, maintenance, and outdoor structures'},
        {'name': 'HVAC', 'description': 'Heating, ventilation, and air conditioning services'},
        {'name': 'Roofing', 'description': 'Roof installation, repair, and maintenance'},
        {'name': 'Cleaning', 'description': 'Deep cleaning, regular maintenance, and specialized cleaning services'}
    ]
    
    created_categories = []
    for category_data in categories:
        category, created = ServiceCategory.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data['description']}
        )
        status = "Created" if created else "Already exists"
        print(f"{status}: {category.name}")
        created_categories.append(category)
    
    return created_categories

def create_alistpro_profiles(alistpro_users, categories):
    """Create A-List Home Pro profiles"""
    print("Creating A-List Home Pro profiles...")
    
    profiles = []
    for i, user in enumerate(alistpro_users):
        # Select 2-3 random categories for each profile
        selected_categories = random.sample(categories, random.randint(2, 3))
        
        profile, created = AListHomeProProfile.objects.get_or_create(
            user=user,
            defaults={
                'business_name': f"{user.name}'s Services",
                'description': f"Professional home services provided by {user.name}.",
                'years_in_business': random.randint(1, 15),
                'service_area': f"City Area {i+1}",
                'is_verified': True if i == 0 else False,
                'average_rating': round(random.uniform(3.5, 5.0), 1)
            }
        )
        
        if created:
            # Add service categories
            profile.service_categories.add(*selected_categories)
            print(f"Created profile for {user.email} with {len(selected_categories)} service categories")
        else:
            print(f"Profile already exists for {user.email}")
        
        profiles.append(profile)
    
    return profiles

def create_portfolios(profiles):
    """Create portfolio items for A-List Home Pro profiles"""
    print("Creating portfolio items...")
    
    portfolio_items = []
    for profile in profiles:
        # Create 2-4 portfolio items for each profile
        for i in range(random.randint(2, 4)):
            item, created = AListHomeProPortfolio.objects.get_or_create(
                alistpro=profile,
                title=f"Project {i+1}",
                defaults={
                    'description': f"Completed project {i+1} for {profile.business_name}.",
                    'image_url': f"https://example.com/portfolio/{profile.id}/{i+1}.jpg",
                    'completed_date': datetime.now() - timedelta(days=random.randint(30, 365))
                }
            )
            
            status = "Created" if created else "Already exists"
            print(f"{status}: Portfolio item for {profile.business_name} - {item.title}")
            portfolio_items.append(item)
    
    return portfolio_items

def create_reviews(profiles, client_users):
    """Create reviews for A-List Home Pro profiles"""
    print("Creating reviews...")
    
    reviews = []
    for profile in profiles:
        # Create 1-3 reviews for each profile
        for i in range(random.randint(1, 3)):
            # Select a random client
            client = random.choice(client_users)
            
            review, created = AListHomeProReview.objects.get_or_create(
                alistpro=profile,
                client=client,
                defaults={
                    'rating': random.randint(3, 5),
                    'comment': f"Great service from {profile.business_name}. Very professional and timely.",
                    'is_verified': random.choice([True, False])
                }
            )
            
            status = "Created" if created else "Already exists"
            print(f"{status}: Review for {profile.business_name} by {client.email}")
            reviews.append(review)
    
    return reviews

def create_appointments(profiles, client_users):
    """Create appointments between clients and A-List Home Pros"""
    print("Creating appointments...")
    
    appointments = []
    for client in client_users:
        # Create 1-2 appointments for each client
        for i in range(random.randint(1, 2)):
            # Select a random profile
            profile = random.choice(profiles)
            
            # Random date in the future
            appointment_date = datetime.now() + timedelta(days=random.randint(1, 30))
            
            # Random status
            status_choices = [
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED
            ]
            status = random.choice(status_choices)
            
            appointment, created = Appointment.objects.get_or_create(
                client=client,
                contractor_profile=profile,
                defaults={
                    'date_time': appointment_date,
                    'duration_minutes': random.choice([30, 60, 90, 120]),
                    'service_description': f"Service request for {profile.business_name}",
                    'status': status,
                    'notes': "Please arrive on time."
                }
            )
            
            status_text = "Created" if created else "Already exists"
            print(f"{status_text}: Appointment between {client.email} and {profile.business_name}")
            appointments.append(appointment)
    
    return appointments

def create_notifications(users):
    """Create notifications for users"""
    print("Creating notifications...")
    
    notifications = []
    
    # Flatten users dict
    all_users = [users['admin']] + users['clients'] + users['alistpros']
    
    for user in all_users:
        # Create 2-5 notifications for each user
        for i in range(random.randint(2, 5)):
            # Random notification type
            notification_types = [
                'MESSAGE', 'APPOINTMENT', 'PAYMENT', 'SYSTEM', 
                'MARKETING', 'REGISTRATION', 'PROFILE_UPDATE',
                'ALISTPRO_ONBOARDING', 'ALISTPRO_VERIFICATION', 'REVIEW'
            ]
            notification_type = random.choice(notification_types)
            
            # Create notification
            notification, created = Notification.objects.get_or_create(
                user=user,
                notification_type=notification_type,
                title=f"Test Notification {i+1}",
                defaults={
                    'message': f"This is a test {notification_type.lower()} notification for {user.email}.",
                    'read': random.choice([True, False]),
                    'delivery_status': random.choice(['PENDING', 'SENT', 'DELIVERED', 'READ'])
                }
            )
            
            status = "Created" if created else "Already exists"
            print(f"{status}: {notification_type} notification for {user.email}")
            notifications.append(notification)
    
    return notifications

def create_conversations(client_users, alistpro_users):
    """Create conversations between clients and A-List Home Pros"""
    print("Creating conversations...")
    
    conversations = []
    for client in client_users:
        # Create a conversation with 1-2 random A-List Home Pros
        for alistpro in random.sample(alistpro_users, random.randint(1, min(2, len(alistpro_users)))):
            conversation, created = Conversation.objects.get_or_create(
                client=client,
                contractor=alistpro
            )
            
            status = "Created" if created else "Already exists"
            print(f"{status}: Conversation between {client.email} and {alistpro.email}")
            
            if created:
                # Add 2-5 messages to the conversation
                for i in range(random.randint(2, 5)):
                    sender = random.choice([client, alistpro])
                    recipient = alistpro if sender == client else client
                    
                    message = Message.objects.create(
                        conversation=conversation,
                        sender=sender,
                        recipient=recipient,
                        content=f"Test message {i+1} from {sender.email} to {recipient.email}",
                        read=random.choice([True, False])
                    )
                    print(f"Created message from {sender.email} to {recipient.email}")
            
            conversations.append(conversation)
    
    return conversations

def main():
    """Main function to create all test data"""
    print("=" * 80)
    print("Creating Test Data for A-List Home Pros Platform".center(80))
    print("=" * 80)
    
    # Create users
    users = create_users()
    
    # Create service categories
    categories = create_service_categories()
    
    # Create A-List Home Pro profiles
    profiles = create_alistpro_profiles(users['alistpros'], categories)
    
    # Create portfolio items
    portfolios = create_portfolios(profiles)
    
    # Create reviews
    reviews = create_reviews(profiles, users['clients'])
    
    # Create appointments
    appointments = create_appointments(profiles, users['clients'])
    
    # Create notifications
    notifications = create_notifications(users)
    
    # Create conversations
    conversations = create_conversations(users['clients'], users['alistpros'])
    
    print("\nTest data creation completed successfully!")
    print(f"Created {len(users['clients'])} clients, {len(users['alistpros'])} A-List Home Pros")
    print(f"Created {len(categories)} service categories")
    print(f"Created {len(profiles)} A-List Home Pro profiles")
    print(f"Created {len(portfolios)} portfolio items")
    print(f"Created {len(reviews)} reviews")
    print(f"Created {len(appointments)} appointments")
    print(f"Created {len(notifications)} notifications")
    print(f"Created {len(conversations)} conversations")

if __name__ == "__main__":
    main()
