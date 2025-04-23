#!/usr/bin/env python
"""
Script to create comprehensive fake data for the A-List Home Pros platform
"""

import os
import django
import random
import string
from datetime import timedelta, datetime, time
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alistpros.settings')
django.setup()

# Import Django models
from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from users.models import UserRole, EmailVerification
from contractors.models import ContractorProfile, ContractorPortfolio, ServiceCategory, ContractorReview
from scheduling.models import AvailabilitySlot, UnavailableDate, Appointment, AppointmentStatus
from messaging.models import Conversation, Message
from notifications.models import Notification, SMSVerification

User = get_user_model()


def generate_random_string(length=10):
    """Generate a random string of letters and digits"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_service_categories():
    """Create service categories if they don't exist"""
    print("\n=== Creating Service Categories ===\n")
    
    categories = [
        "Plumbing", "Electrical", "HVAC", "Carpentry", "Painting", 
        "Landscaping", "Cleaning", "Roofing", "Flooring", 
        "General Contracting", "Handyman", "Appliance Repair"
    ]
    
    created_categories = []
    for category_name in categories:
        category, created = ServiceCategory.objects.get_or_create(name=category_name)
        status = "Created" if created else "Already exists"
        print(f"{status}: {category.name}")
        created_categories.append(category)
    
    return created_categories


def create_users():
    """Create users with different roles"""
    print("\n=== Creating Users ===\n")
    
    # Create admin if it doesn't exist
    try:
        admin = User.objects.get(email="admin@alistpros.com")
        print(f"Admin already exists: {admin.email}")
    except User.DoesNotExist:
        admin = User.objects.create_user(
            email="admin@alistpros.com",
            name="Admin User",
            phone_number="1234567890",
            password="admin123",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            email_verified=True
        )
        print(f"Created admin: {admin.email}")
    
    # Create clients
    clients = []
    client_data = [
        {"email": "client1@example.com", "name": "John Client", "phone": "2345678901"},
        {"email": "client2@example.com", "name": "Sarah Client", "phone": "2345678902"},
        {"email": "client3@example.com", "name": "Mike Client", "phone": "2345678903"},
        {"email": "client4@example.com", "name": "Emma Client", "phone": "2345678904"},
        {"email": "client5@example.com", "name": "David Client", "phone": "2345678905"},
    ]
    
    for data in client_data:
        try:
            client = User.objects.get(email=data["email"])
            print(f"Client already exists: {client.email}")
        except User.DoesNotExist:
            client = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                phone_number=data["phone"],
                password="client123",
                role=UserRole.CLIENT,
                is_verified=True,
                email_verified=True
            )
            print(f"Created client: {client.email}")
        clients.append(client)
    
    # Create contractors
    contractors = []
    contractor_data = [
        {"email": "contractor1@example.com", "name": "Bob Contractor", "phone": "3456789001"},
        {"email": "contractor2@example.com", "name": "Alice Contractor", "phone": "3456789002"},
        {"email": "contractor3@example.com", "name": "Dave Contractor", "phone": "3456789003"},
        {"email": "contractor4@example.com", "name": "Linda Contractor", "phone": "3456789004"},
        {"email": "contractor5@example.com", "name": "Mark Contractor", "phone": "3456789005"},
    ]
    
    for data in contractor_data:
        try:
            contractor = User.objects.get(email=data["email"])
            print(f"Contractor already exists: {contractor.email}")
        except User.DoesNotExist:
            contractor = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                phone_number=data["phone"],
                password="contractor123",
                role=UserRole.CONTRACTOR,
                is_verified=True,
                email_verified=True
            )
            print(f"Created contractor: {contractor.email}")
        contractors.append(contractor)
    
    # Create crew members
    crew_members = []
    crew_data = [
        {"email": "crew1@example.com", "name": "Alex Crew", "phone": "4567890001"},
        {"email": "crew2@example.com", "name": "Taylor Crew", "phone": "4567890002"},
        {"email": "crew3@example.com", "name": "Jordan Crew", "phone": "4567890003"},
    ]
    
    for data in crew_data:
        try:
            crew = User.objects.get(email=data["email"])
            print(f"Crew member already exists: {crew.email}")
        except User.DoesNotExist:
            crew = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                phone_number=data["phone"],
                password="crew123",
                role=UserRole.CREW,
                is_verified=True,
                email_verified=True
            )
            print(f"Created crew member: {crew.email}")
        crew_members.append(crew)
    
    # Create specialists
    specialists = []
    specialist_data = [
        {"email": "specialist1@example.com", "name": "Pat Specialist", "phone": "5678900001"},
        {"email": "specialist2@example.com", "name": "Casey Specialist", "phone": "5678900002"},
    ]
    
    for data in specialist_data:
        try:
            specialist = User.objects.get(email=data["email"])
            print(f"Specialist already exists: {specialist.email}")
        except User.DoesNotExist:
            specialist = User.objects.create_user(
                email=data["email"],
                name=data["name"],
                phone_number=data["phone"],
                password="specialist123",
                role=UserRole.SPECIALIST,
                is_verified=True,
                email_verified=True
            )
            print(f"Created specialist: {specialist.email}")
        specialists.append(specialist)
    
    return {
        "admin": admin,
        "clients": clients,
        "contractors": contractors,
        "crew_members": crew_members,
        "specialists": specialists
    }


def create_contractor_profiles(contractors, categories):
    """Create contractor profiles for contractor users"""
    print("\n=== Creating Contractor Profiles ===\n")
    
    profiles = []
    for i, contractor in enumerate(contractors):
        try:
            profile = ContractorProfile.objects.get(user=contractor)
            print(f"Contractor profile already exists for: {contractor.email}")
        except ContractorProfile.DoesNotExist:
            profile = ContractorProfile.objects.create(
                user=contractor,
                business_name=f"{contractor.name}'s {random.choice(['Services', 'Company', 'Enterprise'])}",
                business_description=f"Professional {random.choice(['home services', 'contracting', 'improvement'])} company with years of experience.",
                years_of_experience=random.randint(1, 20),
                license_number=f"LIC-{generate_random_string(8)}" if random.choice([True, False]) else "",
                insurance_info=f"Insured with {random.choice(['ABC', 'XYZ', 'Best'])} Insurance" if random.choice([True, False]) else "",
                service_radius=random.randint(20, 100),
                is_onboarded=True
            )
            print(f"Created contractor profile for: {contractor.email}")
            
            # Add service categories (2-4 random categories)
            num_categories = random.randint(2, 4)
            selected_categories = random.sample(categories, num_categories)
            profile.service_categories.add(*selected_categories)
            
        profiles.append(profile)
    
    return profiles


# Skipping service creation as it seems the Service model might not be defined in the current system
def create_services(contractor_profiles, categories):
    """Create services offered by contractors - skipped for now"""
    print("\n=== Skipping Services Creation ===\n")
    print("The Service model doesn't appear to be defined in the current system.")


def create_portfolio_items(contractor_profiles):
    """Create portfolio items for contractors"""
    print("\n=== Creating Portfolio Items ===\n")
    
    for profile in contractor_profiles:
        # Create 2-4 portfolio items per contractor
        num_items = random.randint(2, 4)
        for i in range(num_items):
            try:
                item = ContractorPortfolio.objects.create(
                    contractor=profile,
                    title=f"Project {i+1}",
                    description=f"Completed project for a satisfied customer. {random.choice(['Renovation', 'Installation', 'Repair', 'Maintenance'])} work.",
                    # Note: In production, you would upload actual images
                    # For now, we'll leave the image field empty
                    completion_date=timezone.now().date() - timedelta(days=random.randint(1, 365))
                )
                print(f"Created portfolio item: {item.title} for {profile.user.name}")
            except IntegrityError:
                print(f"Portfolio item already exists: Project {i+1} for {profile.user.name}")


def create_reviews(clients, contractor_profiles):
    """Create reviews for contractors"""
    print("\n=== Creating Reviews ===\n")
    
    for profile in contractor_profiles:
        # Create 1-3 reviews per contractor
        num_reviews = random.randint(1, 3)
        reviewers = random.sample(clients, min(num_reviews, len(clients)))
        
        for i, client in enumerate(reviewers):
            try:
                rating = random.randint(3, 5)  # Mostly positive reviews (3-5 stars)
                review = ContractorReview.objects.create(
                    contractor=profile,
                    client=client,
                    rating=rating,
                    comment=f"{'Excellent' if rating == 5 else 'Good' if rating == 4 else 'Satisfactory'} service. {random.choice(['Would recommend.', 'Professional work.', 'Completed on time.', 'Fair pricing.'])}"
                )
                print(f"Created review: {rating} stars from {client.name} for {profile.user.name}")
            except IntegrityError:
                print(f"Review already exists from {client.name} for {profile.user.name}")


def create_availability(contractor_profiles):
    """Create availability schedules for contractors"""
    print("\n=== Creating Availability Schedules ===\n")
    
    day_mapping = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }
    
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for profile in contractor_profiles:
        # Determine which days the contractor works
        working_days = random.sample(days_of_week, random.randint(5, 7))
        
        for day in working_days:
            # Random start time between 7am and 10am
            start_hour = random.randint(7, 10)
            start_time = time(start_hour, 0)
            
            # Random end time between 4pm and 7pm
            end_hour = random.randint(16, 19)
            end_time = time(end_hour, 0)
            
            try:
                availability = AvailabilitySlot.objects.create(
                    contractor=profile,
                    day_of_week=day_mapping[day],
                    start_time=start_time,
                    end_time=end_time,
                    is_recurring=True
                )
                print(f"Created availability: {day.capitalize()} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} for {profile.user.name}")
            except IntegrityError:
                print(f"Availability already exists for {day} for {profile.user.name}")
        
        # Create some unavailable dates
        num_unavailable = random.randint(1, 3)
        for i in range(num_unavailable):
            # Random date in the next 30 days
            unavailable_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
            
            try:
                UnavailableDate.objects.create(
                    contractor=profile,
                    date=unavailable_date,
                    reason=random.choice(["Personal", "Vacation", "Other Commitment", "Training"])
                )
                print(f"Created unavailable date: {unavailable_date} for {profile.user.name}")
            except IntegrityError:
                print(f"Unavailable date already exists for {unavailable_date} for {profile.user.name}")


def create_appointments(clients, contractor_profiles):
    """Create appointments between clients and contractors"""
    print("\n=== Creating Appointments ===\n")
    
    statuses = [
        AppointmentStatus.REQUESTED,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED
    ]
    
    for profile in contractor_profiles:
        # Get service categories for this contractor
        service_categories = profile.service_categories.all()
        if not service_categories:
            print(f"No service categories for {profile.user.name}, skipping appointments")
            continue
            
        # Create 2-4 appointments per contractor
        num_appointments = random.randint(2, 4)
        appointment_clients = random.sample(clients, min(num_appointments, len(clients)))
        
        for client in appointment_clients:
            # Random date in the next 30 days
            appointment_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
            
            # Random start time between 9am and 3pm
            start_hour = random.randint(9, 15)
            start_time = time(start_hour, 0)
            
            # End time 1-3 hours after start time
            duration_hours = random.randint(1, 3)
            end_hour = min(start_hour + duration_hours, 23)
            end_time = time(end_hour, 0)
            
            status = random.choice(statuses)
            service_category = random.choice(list(service_categories))
            
            try:
                appointment = Appointment.objects.create(
                    client=client,
                    contractor=profile,
                    service_category=service_category,
                    appointment_date=appointment_date,
                    start_time=start_time,
                    end_time=end_time,
                    status=status,
                    notes=f"Appointment for {random.choice(['repair', 'installation', 'consultation', 'maintenance'])}.",
                    location=f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar'])} St, Anytown, USA",
                    estimated_cost=Decimal(str(random.randint(50, 500)))
                )
                print(f"Created appointment: {appointment_date} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} between {client.name} and {profile.user.name}")
                
                # Add appointment notes
                if random.choice([True, False]):
                    from scheduling.models import AppointmentNote
                    AppointmentNote.objects.create(
                        appointment=appointment,
                        user=client if random.choice([True, False]) else profile.user,
                        note=random.choice([
                            "Please bring all necessary tools.",
                            "The gate code is 1234.",
                            "Please call when you arrive.",
                            "The issue is in the upstairs bathroom.",
                            "I'll need an estimate before work begins."
                        ]),
                        is_private=random.choice([True, False])
                    )
                    print(f"Added note to appointment {appointment.id}")
                    
            except IntegrityError:
                print(f"Appointment already exists for {appointment_date} {start_time.strftime('%H:%M')} between {client.name} and {profile.user.name}")


def create_conversations_and_messages(clients, contractors):
    """Create conversations and messages between clients and contractors"""
    print("\n=== Creating Conversations and Messages ===\n")
    
    for client in clients[:3]:  # Limit to first 3 clients
        for contractor in contractors[:3]:  # Limit to first 3 contractors
            try:
                # Create conversation
                conversation = Conversation.objects.create(
                    title=f"Conversation between {client.name} and {contractor.name}"
                )
                # Add participants
                conversation.participants.add(client, contractor)
                
                print(f"Created conversation between {client.name} and {contractor.name}")
                
                # Create 3-6 messages in the conversation
                num_messages = random.randint(3, 6)
                for i in range(num_messages):
                    sender = client if i % 2 == 0 else contractor
                    
                    if i == 0:
                        content = f"Hello, I'm interested in your services. Are you available for a {random.choice(['repair', 'installation', 'consultation'])}?"
                    elif i == 1:
                        content = f"Hi {client.name}, yes I am available. What specifically do you need help with?"
                    else:
                        content = random.choice([
                            "Can you provide a quote for this job?",
                            "When would you be available to start?",
                            "I'm available next week if that works for you.",
                            "Do you have any references I can check?",
                            "I've worked on similar projects before.",
                            "What is your hourly rate?",
                            "How long do you think this will take?",
                            "I'll need to check my schedule and get back to you.",
                            "That sounds good to me.",
                            "Let me know if you have any other questions."
                        ])
                    
                    message = Message.objects.create(
                        conversation=conversation,
                        sender=sender,
                        content=content
                    )
                    
                    # Mark as read by the other participant if sender is contractor
                    if sender == contractor:
                        message.read_by.add(contractor)
                        if random.choice([True, False]):
                            message.read_by.add(client)
                    else:
                        # If client is sender, contractor might have read it
                        if random.choice([True, False]):
                            message.read_by.add(contractor)
                    
                    print(f"Created message from {sender.name} in conversation {conversation.id}")
            except IntegrityError:
                print(f"Failed to create conversation between {client.name} and {contractor.name}")


def create_notifications(users_dict):
    """Create notifications for users"""
    print("\n=== Creating Notifications ===\n")
    
    all_users = []
    all_users.extend(users_dict["clients"])
    all_users.extend(users_dict["contractors"])
    all_users.extend(users_dict["crew_members"])
    all_users.extend(users_dict["specialists"])
    
    notification_types = [
        'MESSAGE',
        'APPOINTMENT',
        'PAYMENT',
        'SYSTEM',
        'MARKETING'
    ]
    
    for user in all_users:
        # Create 1-3 notifications per user
        num_notifications = random.randint(1, 3)
        
        for i in range(num_notifications):
            notification_type = random.choice(notification_types)
            
            if notification_type == 'MESSAGE':
                title = "New Message"
                message = "You have received a new message. Check your inbox."
            elif notification_type == 'APPOINTMENT':
                title = "Appointment Update"
                message = random.choice([
                    "New appointment request.",
                    "Your appointment has been confirmed.",
                    "An appointment has been rescheduled.",
                    "An appointment has been cancelled."
                ])
            elif notification_type == 'PAYMENT':
                title = "Payment Update"
                message = random.choice([
                    "Payment received for your services.",
                    "Your payment has been processed.",
                    "Invoice has been generated for your recent service."
                ])
            elif notification_type == 'MARKETING':
                title = "Special Offer"
                message = random.choice([
                    "Limited time offer: 10% off your next service!",
                    "Refer a friend and get a discount on your next appointment.",
                    "New services available in your area."
                ])
            else:  # SYSTEM
                title = "System Notification"
                message = random.choice([
                    "Your account has been updated.",
                    "Password reset requested.",
                    "Your profile information has been updated.",
                    "Please verify your email address."
                ])
            
            try:
                notification = Notification.objects.create(
                    user=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    read=random.choice([True, False]),
                    email_status=random.choice(['PENDING', 'SENT', 'DELIVERED', 'READ']),
                    sms_status='PENDING',
                    push_status=random.choice(['PENDING', 'SENT', 'DELIVERED'])
                )
                print(f"Created {notification_type} notification for {user.name}")
            except IntegrityError:
                print(f"Failed to create notification for {user.name}")
                
        # Create SMS verification for some users
        if random.choice([True, False]):
            try:
                verification_code = ''.join(random.choices(string.digits, k=6))
                expires_at = timezone.now() + timedelta(minutes=30)
                
                sms_verification = SMSVerification.objects.create(
                    user=user,
                    phone_number=user.phone_number,
                    verification_code=verification_code,
                    expires_at=expires_at
                )
                print(f"Created SMS verification code for {user.name}: {verification_code}")
            except IntegrityError:
                print(f"Failed to create SMS verification for {user.name}")


def create_email_verifications(users_dict):
    """Create email verification tokens for users"""
    print("\n=== Creating Email Verification Tokens ===\n")
    
    all_users = []
    all_users.extend(users_dict["clients"])
    all_users.extend(users_dict["contractors"])
    all_users.extend(users_dict["crew_members"])
    all_users.extend(users_dict["specialists"])
    
    for user in all_users:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        expires_at = timezone.now() + timedelta(days=7)
        
        try:
            verification, created = EmailVerification.objects.get_or_create(
                user=user,
                defaults={
                    'token': token,
                    'expires_at': expires_at
                }
            )
            
            if not created:
                verification.token = token
                verification.expires_at = expires_at
                verification.save()
                
            print(f"{'Created' if created else 'Updated'} email verification token for {user.email}: {token}")
        except IntegrityError:
            print(f"Failed to create email verification for {user.email}")


if __name__ == "__main__":
    print("A-List Home Pros Comprehensive Fake Data Generator")
    
    # Create service categories
    categories = create_service_categories()
    
    # Create users
    users = create_users()
    
    # Create contractor profiles
    contractor_profiles = create_contractor_profiles(users["contractors"], categories)
    
    # Create services
    create_services(contractor_profiles, categories)
    
    # Create portfolio items
    create_portfolio_items(contractor_profiles)
    
    # Create reviews
    create_reviews(users["clients"], contractor_profiles)
    
    # Create availability
    create_availability(contractor_profiles)
    
    # Create appointments
    create_appointments(users["clients"], contractor_profiles)
    
    # Create conversations and messages
    create_conversations_and_messages(users["clients"], users["contractors"])
    
    # Create notifications
    create_notifications(users)
    
    # Create email verifications
    create_email_verifications(users)
    
    print("\n=== Fake Data Creation Complete ===\n")
    print("You can now access the admin panel at http://127.0.0.1:8000/admin/")
    print("Login with admin@alistpros.com / admin123")
